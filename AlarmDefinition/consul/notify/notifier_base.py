import abc
from utils import *


class NotifierBase():
    __metaclass__ = abc.ABCMeta

    def __init__(self, inst_name, jtbuf):
        """ """
        self.inst_name = inst_name
        self.jtbuf = jtbuf
        Debug.init_debug(self.inst_name)

        self.retry_counter = 0
        self.remain_data = None

    # public interface
    def notify(self, jdata):
        """ xxxx """
        # 1) merge data
        # print("before merge data: %s" % json_dumps4(jdata))
        Debug.notice("merging %s" % self.inst_name)
        jdata = self._merge_data(jdata)
        if not jdata or len(jdata) <= 0:
            return
        # print("merge data: %s" % json_dumps4(jdata))

        # 2) notify to target
        Debug.notice("send notify to %s" % self.inst_name);
        remain_data = self._send_notify(jdata)
        if not remain_data:
            # success: remove retry_counter by component name
            self.__clear_retry_counter()
            return

        # 3) send failed, write back to jitter_buffer
        Debug.error("send %s %s failed, retried %d" %
                    (self.inst_name, str(remain_data.keys()),
                     self.retry_counter))
        if self.__encrease_retry_counter() <= 3:
            Debug.notice("write '%s' back to jitter_buffer" %
                         self.inst_name)

            # write back to jitter_buffer.
            remain_data = {"Type": self.inst_name,
                           "Value": remain_data}
            self.jtbuf.push(remain_data)

    def get_service_ip_port(self, hostname, service_key):
        consul_ipport = get_consul_address()
        reqfile = "/v1/catalog/service/" + service_key
        Debug.notice("querying service: {0}".format(service_key))
        jdata = http_get_request(consul_ipport, reqfile)
        if Debug.get_debug(self.inst_name):
            Debug.debug("query components service: %s" % json_dumps4(jdata))

        ''' http response shall like:
        [{
            ...
            "ServiceID": "{hostname1}_{component}",
            "ServiceName": "{component}",
            "ServiceTags": ["hostname"],
            "ServiceAddress": "{ip}",
            "ServicePort": {port},
            ...
         }, ...]
         '''
        if not type(jdata) is type([]):
            Debug.error("Bad data type(requied []): %s" % str(type(jdata)))
            return None

        key_id = str(hostname) + "_" + service_key
        for it in jdata:
            if not type(it) is type({}):
                Debug.error("Bad data type(requied {}): %s" % str(type(it)))
                return None

            # match ServiceName
            if not "ServiceName" in it.keys() or service_key != it["ServiceName"]:
                continue
            # match ServiceID
            if not "ServiceID" in it.keys() or key_id != it["ServiceID"]:
                continue

            # extract ip:port
            if "ServiceAddress" in it.keys() and "ServicePort" in it.keys():
                ipaddr = it["ServiceAddress"]
                port = it["ServicePort"]
                if not ipaddr:
                    # FIXME
                    ipaddr = "127.0.0.1"
                return ipaddr + ":" + str(port)

        # not found!
        return None  # "127.0.0.1:3000"

    def put_req_by_http2(self, ipport, jdata, reqfile):
        ''' put diff data to components by http2
            Return True if success, otherwise False
        '''
        retval = False
        try:
            tmpfile = "/tmp/diff_data.json"

            # write to tmp file
            fo = open(tmpfile, "wb")
            fo.write(json.dumps(jdata).encode("UTF-8"))
            fo.close()

            # get nghttp
            nghttp = '/opt/libnghttp2/bin/nghttp'
            if not os.path.exists("/opt/libnghttp2/bin/nghttp"):
                nghttp = 'nghttp'

            # put to host
            reqcmd = "%s -d '%s' http://%s%s" % (
                nghttp, tmpfile, ipport, reqfile)
            resp = os.popen(reqcmd, "r").read()
            Debug.notice("PUT data to http://%s%s response: %.65s" %
                         (ipport, reqfile, resp))

            # check response
            if resp:
                retval = True;
        except Exception as err:
            Debug.fatal("%%Error post_req: %s" % (err))
        return retval

    def __clear_retry_counter(self):
        ''' clear component retry_counter '''
        self.retry_counter = 0

    def __encrease_retry_counter(self):
        ''' encrease component retry_counter
            Return the retry_counter
        '''
        if self.retry_counter > 3:
            self.retry_counter = 0

        self.retry_counter += 1
        return self.retry_counter

    @abc.abstractmethod
    def _merge_data(self, jdata):
        ''' Virtual Method.
            Merge input array into a map structure.

            The input data fortmat:
            [
                {
                "AnyName": AnyValue,
                ...
                }, ...
            ]

            The output data fortmat:
            {
                "AnyName": AnyValue,
                ...
            }
        '''

    @abc.abstractmethod
    def _send_notify(self, jdata):
        ''' Virtual Method.
            Send data to target.

            Return None if success, otherwise return the data list
            of send failed.

            The input and output data fortmat are:
            {
                "AnyName": AnyValue,
                ...
            }
        '''
