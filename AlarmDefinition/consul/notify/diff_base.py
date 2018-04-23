import abc
from utils import *

''' debug purpose '''
class DiffBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, inst_name, jtbuf, cache2file=False, require_initdata=True):
        ''' 
        cache2file       - whether sub class need save cache to file
        require_initdata - whether sub class required consul has init data
        '''
        self.inst_name = inst_name
        self.jtbuf = jtbuf
        self.watch_cache = None
        self.cache_file = None
        Debug.init_debug(self.inst_name)

        # load last data cached in file
        if cache2file:
            self.cache_file = "{0}/{1}_cache.json".format(
                              get_notify_data_path(), self.inst_name)
            Debug.notice("Loading %s cache from file %s" %
                         (self.inst_name, self.cache_file))
            self.watch_cache = self.__load_cache_from_file()

        consul_ipport  = get_consul_address()
        Debug.notice("consul_url: {0}".format(consul_ipport))

        # retry until cache init done
        reqfile = "/v1/kv/cm/values/{0}/{1}?recurse".format(
                  get_consul_version_node(), inst_name)
        while not self.__init_cache(consul_ipport, reqfile, require_initdata):
            Debug.error("Error: diff_manager cache_init failed, try again")
            time.sleep(3)
        Debug.notice("differ %s init done" % inst_name)

    # public interface
    def make_diff(self, jdata):
        """ calculate diff """
        # 1) analyze data
        jdata = self._analyze_data(jdata);
        if not jdata or len(jdata) <= 0:
            return False;

        # 2) calculate_diff
        diff_data = self._calculate_diff(jdata)
        if not diff_data or len(diff_data) <= 0:
            return False;

        # log debug
        if Debug.get_debug(self.inst_name) or Debug.get_debug("diff_data"):
            Debug.debug("diff_data: %s" % (json_dumps4(diff_data)))
        if Debug.get_debug(self.inst_name):
            Debug.debug("diff_cache: %s" % json_dumps4(diff_data))

        # no diff found
        if (not diff_data or len(diff_data) <= 0 or
            not "Value" in diff_data.keys() or len(diff_data["Value"]) <= 0):
            Debug.notice("has no diff data found");
            return False;

        # 3) update cache and save to cache file
        self._update_cache(jdata)

        # 4) push diff into jitter_buffer
        Debug.notice("push to jitter_buffer ...");
        self.jtbuf.push(diff_data)

        return True

    def _update_cache(self, jdata):
        ''' update cache '''
        # update memory cache and save to cache file
        self.watch_cache = jdata
        self.__save_cache_to_file();

    def __save_cache_to_file(self):
        ''' save data to cache '''
        if not self.cache_file:
            return None;

        try:
            with open(self.cache_file, "w") as f:
                data = json_dumps(self.watch_cache)
                f.write(data.encode("UTF-8"))
        except Exception as err:
            Debug.error("Write cache file %s err: %s" %
                       (self.cache_file, str(err)))
            return False
        return True

    def __load_cache_from_file(self):
        ''' load data cache cache '''
        if not self.cache_file:
            return None;
        if not os.path.exists(self.cache_file):
            Debug.error("Not found %s cache file: %s ..." %
                     (self.inst_name, self.cache_file))
            return None;

        # load json file
        Debug.notice("Loading %s cache file: %s ..." %
                     (self.inst_name, self.cache_file))
        jdata = None
        try:
            with open(self.cache_file, "r") as f:
                data = f.read()
            jdata = json.loads(data)
        except Exception as err:
            Debug.error("Load cache file %s err: %s" %
                       (self.cache_file, str(err)))
        return jdata

    def __init_cache(self, consul_ipport, reqfile, require_initdata):
        """ init cache """

        # 1) get data from consul
        jdata = http_get_request(consul_ipport, reqfile)
        if require_initdata and (not jdata or len(jdata) <= 0):
            return False;

        # 2) compare local cache with inital data from consul
        #    If init data has beed load from cache_file,
        #    finding out diff which is updated during this process down.
        if self.watch_cache and len(self.watch_cache) > 0:
            self.make_diff(jdata)
        else:
            # This is the first times loading from consul, or cache_file
            # be removed.
            # Update local cache with this data
            jdata = self._analyze_data(jdata)
            if not jdata or len(jdata) <= 0:
                return False
            self._update_cache(jdata)

        if not self.watch_cache or len(self.watch_cache) <= 0:
            return False
        return True

    @abc.abstractmethod
    def _analyze_data(self, jdata):
        ''' Virtual Method.
            Convert consul output into a searchable map structure.

            The raw input data format:
            [{
                "LockIndex": 0,
                "Key": "cm/values/1.0/components/AllPhone/cluster/IPVersionPreference",
                "Flags": 0,
                "Value": "eyJWYWx1ZSI6IklQdjQifQ==",
                "CreateIndex": 552,
                "ModifyIndex": 552
            }, ...]

            The output data format, 'Value' type depends on 'Type':
            {
                "Type": "{components | system | datastorages, ...}",
                "Value": {
                    "AnyName": AnyValue,
                    ...
                }
            }
        '''

    @abc.abstractmethod
    def _calculate_diff(self, jdata):
        """ Virtual Method.
            Calculate diff for specifical class.

            The input format is the output of _analyze_data().
            The returned data format is same to input.
            {
                "Type": "{components | system | datastorages, ...}",
                "Value": {
                    "AnyName": AnyValue,
                    ...
                }
            }
        """



