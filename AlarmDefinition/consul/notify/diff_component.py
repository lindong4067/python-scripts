import abc
from utils import *
from diff_base import DiffBase

class DiffComponent(DiffBase):
    def __init__(self, jtbuf, cache2file = True):
        ''' init parent '''
        self.inst_name = "components"
        super(DiffComponent, self).__init__(self.inst_name, jtbuf, cache2file)

    def __path_sanity_check(self, keys):
        ''' verify request path '''
        if (len(keys) < 7 or not keys[5] in {"cluster", "server"}):
            return False
        if (len(keys) == 7 and keys[5] != "cluster"):
            return False
        if (keys[3] != self.inst_name):
            return False
        return True

    def _analyze_data(self, jdata):
        ''' _analyze data and output the grouped pairs by component/parameter.
            Key Rule:
            cm/values/{version-node}/components/{component}/cluster/{parameter}/
            cm/values/{version-node}/components/{component}/server/{host}/{parameter}/

            The raw input data format:
            [{
                "LockIndex": 0,
                "Key": "cm/values/1.0/components/AllPhone/cluster/IPVersionPreference",
                "Flags": 0,
                "Value": "eyJWYWx1ZSI6IklQdjQifQ==",
                "CreateIndex": 552,
                "ModifyIndex": 552
            }, ...]

            The returned data format:
            {
                "Type": "components",
                "Value": {
                    "AllPhone": {                               # Component Name
                        "cluster/MLPReceiverPortName": {        # Parameter Path
                            "ModifyIndex": 556,                 # ModifyIndex
                            "Value": "eyJWYWx1ZSI6Ik1M..."      # Value
                        }, ...
                    }, ...
                }
            }
        '''
        values = {}
        for it in jdata:
            #basic type check
            if not type(it) is type({}):
                Debug.error("Bad input data type: %s" % str(type(it)))
                continue

            # prefix check
            key = it["Key"]
            if not key.startswith("cm/values/"):
                Debug.error("Bad input prefix: %s" % key)
                continue;

            # "cm/values/1.0/components/{component}/cluster/{parameter}"
            # "cm/values/1.0/components/{component}/server /{host}/parameter"
            #  0  1      2   3           4          5        6     7
            #
            keys = key.split("/");

            # basic path check
            if not self.__path_sanity_check(keys):
                Debug.error("Bad input key: %s, %s" % (key, str(keys)))
                continue

            # make component name and parameter
            component = keys[4]
            parameter = keys[5] + "/" + keys[6];
            if (keys[5] == "server"):
                # parameter is not for this host!!!, ignore
                if get_hostname() != keys[6]:
                    continue;
                parameter = parameter + "/" + keys[7]

            # decode base64 encoded value
            value = it["Value"]
            if (value and '' != value):
                value = base64decode(value)

            # append parameter values
            jobj = {"Value": value,
                    "ModifyIndex": it["ModifyIndex"]};
            if (component in values.keys()):
                values[component][parameter] = jobj;
            else:
                values[component] = {parameter: jobj}

        values = {"Type": self.inst_name, "Value": values}
        return values

    def _calculate_diff(self, new_data):
        ''' calculate_diff for component
            The input format is the output of _analyze_data().
            The returned data format is same to input.
        '''

        # FIXME: abstract sanity check for all type
        # sanity check
        ## if (self.watch_cache):
        ##     return None;
        ## cache_keys = self.watch_cache.keys()
        ## if not "Type" in cache_keys or not "Value" in cache_keys:
        ##     return None;

        jdata = new_data["Value"]
        jcache = self.watch_cache["Value"]
        if not jcache or not type(jcache) is type({}):
            return None;

        values = {}

        # foreach component
        for comp_key, comp_val in jdata.items():
            # Warning: component not exists in jcache, add it.
            if not comp_key in jcache.keys():
                values[comp_key] = comp_val
                continue

            # foreach parameter
            for param_key, param_val in comp_val.items():
                # Warning: parameter not exists in component, add it.
                # This shall for {component}/server/{host}/parameter,
                # or other case: such as add new parameter.
                if not param_key in jcache[comp_key].keys():
                    Debug.notice("Diff detect add: %s/%s" %
                                 (comp_key, param_key))
                    if (comp_key in values.keys()):
                        values[comp_key][param_key] = param_val;
                    else:
                        values[comp_key] = {param_key: param_val}
                    continue

                # Compare by ModifyIndex and Value.
                cache_val = jcache[comp_key][param_key]
                if ((param_val["ModifyIndex"] != cache_val["ModifyIndex"])
                    and (type(param_val["Value"]) != type(cache_val["Value"])
                         or (param_val["Value"] != cache_val["Value"]))
                    ):
                    if (comp_key in values.keys()):
                        values[comp_key][param_key] = param_val;
                    else:
                        values[comp_key] = {param_key: param_val}

        values = {"Type": self.inst_name, "Value": values}
        return values

