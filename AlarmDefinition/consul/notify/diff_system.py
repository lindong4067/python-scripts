import abc
from utils import *
from diff_base import DiffBase

class DiffSystem(DiffBase):
    def __init__(self, jtbuf, cache2file = True):
        ''' init parent '''
        self.inst_name = "system"
        super(DiffSystem, self).__init__(self.inst_name, jtbuf, cache2file)

    def __path_sanity_check(self, keys):
        ''' verify request path '''
        if (len(keys) < 6 or not keys[4] in {"cluster", "server"}):
            return False
        if (len(keys) == 6 and keys[4] != "cluster"):
            return False
        if (keys[3] != self.inst_name):
            return False
        return True

    def _analyze_data(self, jdata):
        ''' _analyze data and output the grouped pairs by component/parameter.
            Key Rule:
            cm/schema/{version-node}/system/cluster/{parameter}
            cm/schema/{version-node}/system/server/{host}/{parameter}

            The raw input data format:
            [{
                "LockIndex": 0,
                "Key": "cm/value/1.0/system/cluster/AnyPhoneForcedLocUpEnabled",
                "Flags": 0,
                "Value": "...",
                "CreateIndex": 552,
                "ModifyIndex": 552
            }, ...]

            The returned data format:
            {
                "Type": "system",
                "Value": {
                    "cluster/AnyPhoneForcedLocUpEnabled": { # Parameter Path
                        "ModifyIndex": 556,                 # ModifyIndex
                        "Value": "..."                      # Value
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

            # "cm/values/1.0/system/cluster/{parameter}"
            # "cm/values/1.0/system/server /{host}/parameter"
            #  0  1      2   3      4       5      6
            #
            keys = key.split("/");

            # basic path check
            if not self.__path_sanity_check(keys):
                Debug.error("Bad input key: %s, %s" % (key, str(keys)))
                continue

            # make parameter
            parameter = keys[4] + "/" + keys[5];
            if (keys[4] == "server"):
                # parameter is not for this host!!!, ignore
                if get_hostname() != keys[5]:
                    continue;
                parameter = parameter + "/" + keys[6]

            # decode base64 encoded value
            value = it["Value"]
            if (value and '' != value):
                value = base64decode(value)

            # append parameter values
            jobj = {"Value": value,
                    "ModifyIndex": it["ModifyIndex"]};
            values[parameter] = jobj

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

        # foreach parameter
        for param_key, param_val in jdata.items():
            # Warning: parameter not exists, add it.
            # This shall for server/{host}/parameter,
            # or other case: such as add new parameter.
            if not param_key in jcache.keys():
                Debug.notice("Diff detect add: %s" % (param_key))
                values[param_key] = param_val;
                continue

            # Compare by ModifyIndex and Value.
            cache_val = jcache[param_key]
            if ((param_val["ModifyIndex"] != cache_val["ModifyIndex"])
                and (type(param_val["Value"]) != type(cache_val["Value"])
                     or (param_val["Value"] != cache_val["Value"]))
                ):
                values[param_key] = param_val;

        values = {"Type": self.inst_name, "Value": values}
        return values

