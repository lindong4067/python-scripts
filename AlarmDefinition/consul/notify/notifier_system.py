import abc
from utils import *
from notifier_base import NotifierBase

class NotifierSystem(NotifierBase):
    def __init__(self, jtbuf):
        ''' init parent '''
        self.inst_name = "system"
        super(NotifierSystem, self).__init__(self.inst_name, jtbuf)

        consul_ipport  = get_consul_address()
        Debug.notice("consul_url: {0}".format(consul_ipport))

        # retry until schema init done
        reqfile = "/v1/kv/cm/schema/{0}/{1}?recurse".format(
                  get_consul_schema_version(), self.inst_name)
        while not self.__init_schema_impacts(consul_ipport, reqfile):
            Debug.error("Error: notifier init schema failed, try again")
            time.sleep(3)

        Debug.notice("notifier %s init done" % self.inst_name)

    def __init_schema_impacts(self, consul_ipport, reqfile):
        """ create components dependance cache by analyze schema in consul
        """
        # 1) get data from consul
        jdata = http_get_request(consul_ipport, reqfile)
        if not jdata or len(jdata) <= 0:
            return False;

        # 2) analyze schema
        jdata = self.__analyze_schema(jdata);
        if not jdata or len(jdata) <= 0:
            return False;

        self.schema_impacts = jdata
        Debug.notice("system schema: %s" % json_dumps4(jdata))
        return True

    def __analyze_schema_value(self, schema_name, schema_val):
        ''' _analyze schema and output the grouped pairs by parameter/components.
            The returned data format:
            {
                "AnyPhoneForcedLocUpEnabled": [     # Parameter Name
                    "AnyPhone",                     # Component Name
                    "TriggerLocation",
                    ...
                    ]
                ...
            }
        '''
        # schema basic analyze
        if not schema_val:
            return None
        #print("xxx: \n\n", schema_val)

        # parse string schema to json object
        jschema = json_parse(schema_val)
        if not jschema:
            Debug.error("Parse schema: %s error: %.35s" %
                        (schema_name, schema_val))
            return None

        # basic check
        if type(jschema) != type({}) or not 'impacts' in jschema:
            Debug.error("Parse schema not found %s" % (schema_name))
            return None

        # sanity check impacts
        impacts = jschema['impacts']
        if type(impacts) != type([]):
            Debug.error("Parse schema %s impacts, bad type: %s" %
                        (schema_name, type(impacts)))
            return None


        # Add new paramter
        values = []

        # foreach component-name in impacts
        for comp_name in impacts:
            values.append(comp_name);

        return values;

    def __analyze_schema(self, jdata):
        ''' get schema from consul and analyze output a searchable list.
            The input data from consul:
            1) Raw data format:
                [{
                    "LockIndex": 0,
                    "Key": "cm/schema/1.0/system/AnyPhoneForcedLocUpEnabled",
                    "Flags": 0,
                    "Value": "eyJkZWZhdWx0X3ZhbHVlIjogIjAiLCAiYW ... =",
                    "CreateIndex": 29244,
                    "ModifyIndex": 29244
                }, ...]

                The value of schema looks like:
                {
                    "impacts":      [               # Impact Component list
                        "AnyPhone",                 # Component Name
                        "TriggerLocation",
                        ...
                        ],
                    "default_value": "0",           # others
                    ...
                }

            3) The returned data format:
            {
                "AnyPhoneForcedLocUpEnabled": [     # Parameter Name
                    "AnyPhone",                     # Component Name
                    "TriggerLocation",
                    ...
                    ]
                ...
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
            if not key.startswith("cm/schema/"):
                Debug.error("Bad scmema prefix: %s" % key)
                continue;

            # "cm/schema/1.0/system/{parameter}"
            #  0  1      2   3      4
            #
            keys = key.split("/");

            # basic path check
            if len(keys) != 5 or keys[3] != self.inst_name:
                Debug.error("Bad scmema key: %s, %s" % (key, str(keys)))
                continue

            # make schema_name
            schema_name = keys[4]

            # decode base64 encoded value
            value = it["Value"]
            if (value and '' != value):
                value = base64decode(value)

            # analyze schema value
            value = self.__analyze_schema_value(schema_name, value)
            if not value:
                continue

            # append parameter values
            values[schema_name] = value

        return values

    def _merge_data(self, jarray):
        ''' merge request in array to components/parameter pairs.
            [   {
                    "cluster/CenterCoordinateLong": {       # Parameter Path
                        "ModifyIndex": 60540,               # ModifyIndex
                        "Value": "..."                      # Value
                    }, ...
                }, {
                    "cluster/CenterCoordinateLat": {
                        "ModifyIndex": 60539,
                        "Value": "..."
                },
                ...
            ]

            The return data format:
            {
                "cluster/CenterCoordinateLong": {       # Parameter Path
                    "ModifyIndex": 60540,               # ModifyIndex
                    "Value": "..."                      # Value
                },
                "cluster/CenterCoordinateLat": {
                    "ModifyIndex": 60539,
                    "Value": "..."
                },
                ...
            }
        '''

        values = {};
        for jdata in jarray:
            # look the first as base
            if 0 == len(values):
                values = jdata
                continue

            # merger: foreach parameter
            for param_key, param_val in jdata.items():
                # parameter not exists in component, add it.
                if not param_key in values.keys():
                    values[param_key] = param_val
                    continue

                # make base value
                base_val = values[param_key]

                # new than base_val, update it
                if (param_val["ModifyIndex"] > base_val["ModifyIndex"]):
                    values[param_key] = param_val;

        return values

    def _send_notify(self, jdata):
        """ Send data to target.

            The 'system' parameters applied to the components which are
            define in schema impacts list. This routine extracts the
            parameters from param_key, making a new component diff
            message and then put back to jitter buffer.

            The components notifier shall pick up the diff message,
            and sending to the target component.
        """

        # foreach parameter:
        Debug.notice("Analyze impacts and push back to jtbuf ...")
        for param_key, param_val in jdata.items():
            # 1) extract parameter name
            #    Attation: Components reqired replace:
            #              a. 'cluster' to 'clustersystem'
            #              b. 'server' to 'serversystem'
            #    So make new_param_key by param_key.
            if param_key.startswith('cluster/'):
                param_name = param_key[8:]
                new_param_key = param_key.replace('cluster', 'clustersystem', 1)
            elif param_key.startswith('server/'):
                new_param_key = param_key.replace('server', 'serversystem', 1)
                param_name = param_key[param_key.rindex('/') + 1:]
            else:
                Debug.error("Bad param_name %s" % param_key)
                continue

            # 2) parameter defined in impacts list
            if not param_name in self.schema_impacts:
                Debug.error("Not found param_name %s in impacts" % param_name)
                continue

            # foreach impacts components
            comp_list = self.schema_impacts[param_name]
            for comp_key in comp_list:
                # 3) make new diff message by impacts components
                Debug.notice("Put %s to %s" % (new_param_key, comp_key))
                jdata = {comp_key: {new_param_key: param_val}}
                values = {"Type": "components", "Value": jdata}

                # 4) push each diff into jitter_buffer
                self.jtbuf.push(values)

        return None

