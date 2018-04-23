#!/usr/bin/env python
# --coding:utf-8--

import os, sys
import time
import getopt
import traceback
import ssl
import json
import urllib2
import getpass

# from urllib import request as urllib2

jtample = {
    "parameter": {
        "cluster": {
            "components": {
                "{component}": {
                    "{name}": "{value}"
                }
            },
            "system_setting": {
                "{name}": "{value}"
            }
        },
        "servers": {
            "{host}": {
                "components": {
                    "{component}": {
                        "{name}": "{value}"
                    }
                },
                "system_setting": {
                    "{name}": "{value}"
                }
            }
        }
    },
    "datastorage": {
        "cluster": {
            "{datastorage}": {
                "{key}": "{value}"
            }
        },
        "servers": {
            "{host}": {
                "{datastorage}": {
                    "{key}": "{value}"
                }
            }
        }
    },
    "schema": {
        "components": {
            "{component}": {
                "{name}": "{value}"
            }
        },
        "system_setting": {
            "{name}": "{value}"
        },
        "datastorages": {
            "{key}": "{value}"
        }
    }
}


class BaseUtils(object):
    def _json_parse(self, data):
        ''' parse json string '''
        try:
            if not data:
                return {}
            return json.loads(data);
        except Exception as err:
            print("%%Error: parse data (%s...) error: %s" % (data, err))
        return {};

    def _json_dumps4(self, jdata):
        ''' dump json string with pretty format '''
        try:
            return json.dumps(jdata, indent=4)
        except Exception as err:
            print("%%Error: dump data error: %s" % (err))
        return "";


class Options(BaseUtils):
    export_arg_opts = [
        ("a", "omcenter", "ip:port", "indicate omcenter address include ip and port"),
        ("u", "username", "string", "omcenter login account\n"),
        # ("p", "password", "string", "omcenter login password\n"),
        ("t", "type", "typename", "indicate export 'parameter', 'datastorage' or 'both'"),
        # ("v", "version", "node-version-cluster", "(Resolved)Indicate which node/version/cluster to export"),
        ("s", "server", "server1;server2;...", "indicate export for which server, or all"),
        ("m", "schema", "", "indicate export schema only"),
        ("l", "split", "", "indicate if split file according to type and level"),
        ("f", "file", "filename", "export path or file name"),
        ("V", "verbose", "", "verbose mode"),
        ("h", "help", "", "show help"),
    ]

    import_arg_opts = [
        ("a", "omcenter", "ip:port", "indicate omcenter address include ip and port"),
        ("u", "username", "string", "omcenter login account\n"),
        # ("p", "password", "string", "omcenter login password\n"),
        ("f", "file", "filename", "import path or file name"),
        ("F", "force", "", "force import file with no confirm"),
        ("S", "sanity-check-only", "", "sanity check the import data only"),
        ("V", "verbose", "", "verbose mode"),
        ("h", "help", "", "show help"),
    ]

    def __init__(self):
        super(Options, self).__init__()
        self.X_AUTH_TOKEN = "X-Auth-Token"
        self.command = ""
        self._options = ""

        # parse args
        self.command, self._options = self._parse_args()
        if not self.command or not self._options:
            self.command = ""

    def debug(self, msg):
        if "verbose" in self._options.keys():
            print("%%%s" % str(msg))

    def warning(self, msg):
        print("%%Warning: %s" % str(msg))

    def error(self, msg):
        print("%%Error: %s" % str(msg))

    def getoption(self, option_name):
        if not self._options or not option_name in self._options.keys():
            return "";
        return self._options[option_name]

    def _export_usage(self, arg_opts):
        print("configdata export [options]")
        for sname, lname, vname, desc in arg_opts:
            lname = (lname if "" == vname else ("%s=%s" % (lname, vname)));
            print(" -%s, --%-30s%s" % (sname, lname, desc.capitalize()));
        return 1;

    def _import_usage(self, arg_opts):
        print ("configdata import [options]")
        for sname, lname, vname, desc in arg_opts:
            lname = (lname if "" == vname else ("%s=%s" % (lname, vname)));
            print(" -%s, --%-30s%s" % (sname, lname, desc.capitalize()));
        return 1;

    def _getopts(self, arg_opts):
        sopt, lopt, l2sopt = "D", [], {}
        for sname, lname, vname, desc in arg_opts:
            sopt += (sname if "" == vname else ("%s:" % sname));
            lopt.append(lname if "" == vname else ("%s=" % lname));
            if "" != lname:
                l2sopt[lname] = sname
        try:
            opts, args = getopt.gnu_getopt(sys.argv[2:], sopt, lopt)
        except getopt.GetoptError as err:
            print("%%Error: %s" % str(err))
            return ([('h', "")], []);

        opr = []
        for op, value in opts:
            sname = (l2sopt[op[2:]] if "--" == op[0:2] else op[1:]);
            opr.append((sname, value))
        return opr, args

    def _export_parse_args(self, arg_opts):
        options = {};
        opts, args = self._getopts(arg_opts);
        for op, value in opts:
            if op == "a":
                options["omcenter"] = value
            elif op == "u":
                options["username"] = value
            elif op == "p":
                options["password"] = value
            elif op == "t":
                if value not in ('parameter', 'datastorage', 'both'):
                    self._export_usage(self.export_arg_opts)
                    return None
                options["type"] = value
            elif op == 's':
                options["server"] = value
            elif op == 'f':
                options["file"] = value
            elif op == 'v':
                options["version"] = value
            elif op == 'l':
                options["split"] = True  # value
            elif op == 'm':
                options["schema"] = True
            elif op == 'V':
                options["verbose"] = True
            elif op == 'D':
                options["debug"] = True
            else:
                # print("Bad option: '%s': '%s'" % (op, value))
                self._export_usage(self.export_arg_opts)
                return None
        if len(args) > 0:
            print("%%Error: unsupport args: %s" % str(args))
            self._export_usage(self.export_arg_opts);
            return None;

        # check required args
        required_args = ("omcenter",)
        for arg in required_args:
            if arg not in options.keys() or not options[arg]:
                # print("%%Error: parameter --%s is required" % arg)
                self._export_usage(self.export_arg_opts);
                return None;

        # set default
        if "type" not in options.keys():
            options["type"] = "both"

        # if "split" in options.keys():
        #    # don't split if filename specified
        #    if "file" in options.keys():
        #        del options["file"]
        #    #elif (options["split"] not in ("level2", "level3")):
        #    #    self._export_usage(self.export_arg_opts);
        #    #    return None;                

        return options

    def _import_parse_args(self, arg_opts):
        options = {};
        opts, args = self._getopts(arg_opts);
        for op, value in opts:
            if op == "a":
                options["omcenter"] = value
            elif op == "u":
                options["username"] = value
            elif op == "p":
                options["password"] = value
            elif op == 'f':
                options["file"] = value
            elif op == 'S':
                options["sanity"] = True
                options["force"] = True
            elif op == 'F':
                options["force"] = True
            elif op == 'V':
                options["verbose"] = True
            elif op == 'D':
                options["debug"] = True
            else:
                # print("Bad option: '%s': '%s'" % (op, value))
                self._import_usage(self.import_arg_opts)
                return None
        if (len(args)) > 0:
            print("Usage: configdata import [file or directory name]")
            self._import_usage(self.import_arg_opts);
            return None
        # check required args
        required_args = ("omcenter",)
        for arg in required_args:
            if arg not in options.keys() or not options[arg]:
                # print("%%Error: parameter --%s is required" % arg)
                self._import_usage(self.import_arg_opts);
                return None;

        return options

    def __command_usage(self):
        print("Usage: configdata [--help] [command] [<args>]\n")
        print("Available command are:")
        print("  export     export configure data")
        print("  import     import configure data")
        print("")

    def _parse_args(self):
        if len(sys.argv) < 2:
            self.__command_usage()
            return None, None;
        command = sys.argv[1];

        if command == "export":
            options = self._export_parse_args(self.export_arg_opts);
        elif command == "import":
            options = self._import_parse_args(self.import_arg_opts);
        else:
            self.__command_usage()
            options = None
        return command, options

    def _login_oam_center(self, username, password):
        oamcenter_addr = self.getoption("omcenter")
        print("\nLogin to %s ..." % oamcenter_addr)

        requrl = ("https://%s/cluster/gmpc/auth/tokens" % oamcenter_addr)
        jdata = {"auth": {
            "method": "password",
            "password": {
                "user_id": username,
                "password": password
            }
        }}
        code, jdata, token = self._omcenter_login_request(requrl, jdata)
        # self.debug("%%response code %d, token %s, msg: %s" % (
        #            code, token, self._json_dumps4(jdata)))

        if 200 != code:
            print("Login to omcenter failed(%d): %s" % (
                code, self._json_dumps4(jdata)))
            return None
        return token

    def _get_login_token(self):
        username = self.getoption("username")
        password = self.getoption("password")

        for retry_num in range(3):
            print("")
            if username == "":
                username = raw_input("Please input username: ")
            password = getpass.getpass("Please input password: ")
            token = self._login_oam_center(username, password)
            if "" != token:
                return token;


# define class for import
class ImportData(Options):
    def __init__(self):
        super(ImportData, self).__init__()
        self.record_counter = 0;
        # self.argopt = argopt

    def _get_csd_file(self, filepath, flist):
        pathDir = os.listdir(filepath)
        json_data = []
        for name in pathDir:
            if name[-4:] != '.csd':
                continue

            fname = ("%s/%s" % (filepath, name))
            flist.append(fname)
            self.debug("merging file: %s" % fname)
            try:
                with open(fname, 'r') as f:
                    data = f.read()
                    jdata = self._json_parse(data)
            except Exception as err:
                print("Error: read file '%s' error: %s" % (
                    fname, str(err)))
                return
            json_data.extend(jdata)
        # print("----", json_data)
        # return
        return json_data

    def _data_sanity_check(self, jdata, jtpl, path):
        if type(jdata) is type(None):
            return True
        dtype = type(jdata)
        if dtype == type(u'abc'):
            dtype = type("abc")
        if not dtype is type(jtpl):
            # datastorage value may be: {} or []
            if (type(jtpl) == type("abc") and (
                    dtype == type({}) or dtype == type([]))):
                pass
            else:
                self.error("bad data format, %s require %s" % (
                    path, str(type(jtpl))))
                return False
        if not type(jtpl) is type({}):
            self.record_counter += 1
            return True
        # print(jtpl.keys())
        for name, jobj in jdata.items():
            tplkeys = jtpl.keys()
            if tplkeys[0][0] == "{" and tplkeys[0][-1] == "}":
                child_jtpl = jtpl[tplkeys[0]]
            else:
                if not name in jtpl.keys():
                    self.error("bad object name: %s/%s, valid name: %s" % (
                        path, name, str(jtpl.keys())))
                    return False
                child_jtpl = jtpl[name]

            # print(jtpl.keys())
            if not self._data_sanity_check(jobj, child_jtpl, path + "/" + name):
                return False
        return True

    def _sanity_check(self, jdata):
        if not type(jdata) is type([]):
            self.error("bad data format, root require []")
            return False
        for jcluster in jdata:
            if not type(jcluster) is type({}):
                self.error("bad data format, cluster require {} ")
                return False
            for cname, jobj in jcluster.items():
                if cname == "version":
                    pass
                elif cname == "data":
                    if not type(jobj) is type({}):
                        self.error("bad data format: data")
                        return False
                elif cname == "errors":
                    pass  # response
                else:
                    self.error("unsupported object name '%s'" % cname)
                    return False

            if not "data" in jcluster.keys():
                self.error("miss object name 'data'")
                return False
            if not self._data_sanity_check(jcluster["data"], jtample, "data"):
                return False
        return True

    def import_file(self):
        options = self._options
        self.debug("%%options: %s" % str(options))

        # default the current path       
        filename = self.getoption("file")
        if not filename:
            filename = "."

        # 1) read from directory
        flist = []
        if os.path.isdir(filename):
            json_data = self._get_csd_file(filename, flist)
        # 2) read from specific filename      
        else:
            # read content from file
            try:
                with open(filename, 'r') as f:
                    data = f.read()
                    json_data = self._json_parse(data);
            except Exception as err:
                print("Error: read file '%s' error: %s" % (
                    filename, str(err)))
                return
            flist.append(filename)
        print("Import files to %s:" % self.getoption("omcenter"))
        for fname in flist:
            print("  %s" % fname)

        # confirm import
        if not self.getoption("force"):
            s = raw_input("Are you sure? [N/y]")
            if ((s == "") or (s not in ['Y', 'y'])):
                return
        # print("Sending files ...")

        print("\nImport data sanity checking ...")
        if not self._sanity_check(json_data):
            return
        print("Sanity check passed!")

        # only do sanity check
        if (self.getoption("sanity")):
            return

        # login and get token failed.
        token = self._get_login_token()
        if None == token or type(token) != type(("")):
            return

        # build requrl
        requrl = "https://%s/configdata" % (self.getoption("omcenter"))
        code, jresp = self._import_request(requrl, json_data, token)
        self.debug("%%response %d: %s" % (code, self._json_dumps4(jresp)))
        if (200 != code):
            print("%%Error: %d: %s" % (code, str(jresp)))
        else:
            if "errors" in jresp:
                ''' Error format like below: {
                    "errmsg": "{general error}"
                    "errors": {
                        "18-GMPC-cluster": {
                            "importDataStorageServers:436": {
                                "errmsg": "java.lang.NullPointerException"
                            }, 
                    }
                } '''
                for cluster, cdata in jresp["errors"].items():
                    print("%%Error: import '%s':" % cluster)
                    for errname, errdata in cdata.items():
                        print("  %s: %s" % (errname, errdata["errmsg"]))
            elif "errmsg" in jresp:
                print("%%Error: %s" % self._json_dumps4(jresp))
            else:
                print("Import data to consul success!")
        success_count = jresp["success_count"]
        print("Summary: Total %d records, %d success, %d failed." %
              (self.record_counter, success_count,
               self.record_counter - success_count))

    def _import_request(self, requrl, json_data, token):
        http_code = 200
        try:
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            # response = urllib2.urlopen(requrl, timeout=1000)

            # self.debug("request data: %s" % self._json_dumps4(json_data))
            request = urllib2.Request(requrl, data=json.dumps(json_data))
            request.add_header("X-Auth-Token", token)
            request.get_method = lambda: 'PUT'
            response = urllib2.urlopen(request)
            data = response.read()
            # print("response %s" % data)
            http_code = response.getcode()
        except urllib2.HTTPError as err:
            # print("%%Error response: %s" % str(err))
            http_code = err.code
            data = err.read()
        except Exception as err:
            return 0, err
        return http_code, self._json_parse(data)


class ConfigData(ImportData):
    def __init__(self):
        super(ConfigData, self).__init__()
        self.write_failed = False
        # self.argopt = argopt

    def _http_get_request2(self, requrl, token):
        import ssl
        from functools import partial
        ssl.wrap_socket = partial(ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1)

        http_code = 400
        curl = "/opt/curl_http2/bin/curl"
        if not os.path.exists("/opt/curl_http2/bin/curl"):
            curl = 'curl'
        reqcmd = ("%s -k -s '%s'" % (curl, requrl))
        # print("reqcmd: %s" % reqcmd)
        data = os.popen(reqcmd, "r").read()
        if not data:
            return http_code, None
        # print("data:--%s--" % data)
        jdata = self._json_parse(data)
        http_code = 200
        return http_code, jdata
        # return http_code, None

    def _http_get_request(self, requrl, token):
        self.debug("GET %s" % requrl)
        http_code = 200
        data = ""
        try:
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            request = urllib2.Request(requrl)
            request.add_header("X-Auth-Token", token)
            response = urllib2.urlopen(request)
            http_code = response.getcode()
            data = response.read()
        except urllib2.HTTPError as err:
            http_code = err.code
            data = err.read()
        except Exception as err:
            return 0, err
        return http_code, self._json_parse(data)

    def _omcenter_login_request(self, requrl, json_data):
        self.debug("PUT %s" % requrl)
        http_code = 200
        data, token = "", ""
        try:
            if hasattr(ssl, '_create_unverified_context'):
                ssl._create_default_https_context = ssl._create_unverified_context
            # response = urllib2.urlopen(requrl, timeout=1000)

            request = urllib2.Request(requrl, data=json.dumps(json_data))
            request.add_header("X-Auth-Token", token)
            request.add_header("Content-Type", "application/json;charset=UTF-8")
            request.get_method = lambda: 'POST'
            response = urllib2.urlopen(request)

            http_code = response.getcode()
            token = response.headers.get(self.X_AUTH_TOKEN)
            data = response.read()
        except urllib2.HTTPError as err:
            http_code = err.code
            data = err.read()
        except Exception as err:
            return 0, err, token
        return http_code, self._json_parse(data), token

    def _save_file(self, filename, jdata):
        try:
            with open(filename, 'w') as f:
                f.write(self._json_dumps4(jdata))
        except Exception as err:
            print("Error: write file '%s' failed: %s" % (
                filename, str(err)))
            self.write_failed = True;
            return
        print("Write to file: %s" % filename)

    def _is_dir_include_csd_file(self, filepath):
        pathDir = os.listdir(filepath)
        for name in pathDir:
            if name[-4:] == '.csd':
                return True
        return False

    def _backup_old_file(self):
        options = self._options
        dirname = self.getoption("file");

        # no dirname
        if not dirname:
            dirname = "."
        if not os.path.isdir(dirname):
            # create new file
            return True
        if not self._is_dir_include_csd_file(dirname):
            return True

        # make backup directory
        timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        bkdirname = dirname + "/old/bk_" + timestamp
        # os.makedirs(dirname + "/old")
        os.makedirs(bkdirname)
        if not os.path.isdir(bkdirname):
            print("%Error: make directory '%s' error!" % dirname)
            return False
        # print("mv " + dirname + "/*.csd " + bkdirname)
        os.system("mv " + dirname + "/*.csd " + bkdirname)
        print("Backup files %s/*.csd to: %s ...\n" % (dirname, bkdirname))

        return True

    def _save_single_file(self, prefix, version, jdata):
        options = self._options

        filename = self.getoption("file");
        def_fname = version + "_" + prefix + ".csd"
        if not filename:
            filename = def_fname
        elif os.path.isdir(filename):
            filename += "/" + def_fname
        # if jdata[0] and "errors" in jdata[0].keys():
        #    del(jdata[0]["errors"])
        self._save_file(filename, jdata)

    def _dict_has(self, jdata, path):
        if not jdata:
            return False
        for key in path.split("/"):
            if type(jdata) != type({}) or key not in jdata.keys():
                return False
            jdata = jdata[key]
        return True

    def _dict_get(self, jdata, path):
        if not jdata:
            return None
        for key in path.split("/"):
            if type(jdata) != type({}) or key not in jdata.keys():
                return None
            jdata = jdata[key]
        return jdata

    def _save_multi_file(self, prefix, version, jdata):
        dirname = self.getoption("file")
        if not dirname:
            dirname = "."

        # save parameter.cluster
        cluster = self._dict_get(jdata, 'data/parameter/cluster')
        if cluster:
            jval = [{"version": version, "data": {
                "parameter": {"cluster": cluster}}}]
            filename = version + "_parameter_cluster.csd"
            self._save_file(dirname + "/" + filename, jval)

        # save parameter.servers
        servers = self._dict_get(jdata, 'data/parameter/servers')
        if servers:
            for name, value in servers.items():
                filename = version + "_parameter_" + name + ".csd"
                jval = [{"version": version, "data": {
                    "parameter": {"servers": {name: value}}}}]
                self._save_file(dirname + "/" + filename, jval)

        # save datastorage.cluster
        cluster = self._dict_get(jdata, 'data/datastorage/cluster')
        if cluster:
            filename = version + "_datastorage_cluster.csd"
            jval = [{"version": version, "data": {
                "datastorage": {"cluster": cluster}}}]
            self._save_file(dirname + "/" + filename, jval)

        # save datastorage.servers
        servers = self._dict_get(jdata, 'data/datastorage/servers')
        if servers:
            for name, value in servers.items():
                filename = version + "_datastorage_" + name + ".csd"
                jval = [{"version": version, "data": {
                    "datastorage": {"servers": {name: value}}}}]
                self._save_file(dirname + "/" + filename, jval)

    def _export_save_file(self, json_data):
        options = self._options
        jdata = json_data[0]
        if type(jdata) != type({}) or not "version" in jdata:
            print("%%Error: Bad response: %s" % (str(jdata)))
            return

        self.debug("Sanity checking the response data ...")
        jtample["errors"] = {"{path}": "value"}
        # print(self._json_dumps4(jtample))
        if not self._sanity_check(json_data):
            return

        # backup files in directory
        if not self._backup_old_file():
            return False

        version = jdata["version"]
        if "schema" in options.keys():
            self._save_single_file("schema", version, [jdata, ]);
        elif "split" in options.keys():
            self._save_multi_file(self.getoption("type"), version, jdata);
        else:
            self._save_single_file(self.getoption("type"), version, [jdata, ]);

        # log errors
        failed_count = 0
        if "errors" in jdata.keys():
            errors = jdata["errors"]
            self.debug("errors: %s" % self._json_dumps4(errors))
            print("")
            self.warning("Export detect following error:")
            for key, value in errors.items():
                print("  %s: %s" % (key, str(value)))
            failed_count = len(errors)

        # summary
        success_count = self.record_counter
        if self.write_failed:
            failed_count += self.record_counter
            success_count = 0
        print("Summary: Total %d records, %d records successfully write to file, %d failed." %
              (self.record_counter, success_count, failed_count))

    def export_file(self):
        options = self._options
        self.debug("%%options: %s" % str(options))
        datatype = self.getoption("type")
        if datatype == "both":
            datatype = "parameter' and 'datastorage"
        if self.getoption("schema"):
            datatype = "schema' for '" + datatype
        print("Export '%s' from %s" % (datatype, self.getoption("omcenter")))
        if self.getoption("split"):
            print("Save data into different files")
        else:
            print("Save data into single file")
        print("")

        # login and get token failed.
        token = self._get_login_token()
        if None == token or type(token) != type(("")):
            return

        # make requrl
        requrl = "https://%s/configdata?type=%s" % (
            self.getoption("omcenter"), self.getoption("type"))

        # FIXME: this option is resolved
        if "version" in options.keys():
            requrl += "&version=" + options["version"]
        if "schema" in options.keys():
            requrl += "&schema=true"
        if "server" in options.keys():
            requrl += "&server=" + options["server"]

        # export request 
        code, jdata = self._http_get_request(requrl, token)
        if "verbose" in options.keys():
            print("%%response: %.*s..." % (50, str(jdata)))
        if "debug" in options.keys():
            print("%%response: %s " % (self._json_dumps4(jdata)))

        if (not jdata or type(jdata) != type([]) or
                not 200 == code or len(jdata) <= 0):
            print("%%Error: omcenter returns failed (%d): %s" % (
                code, str(jdata)))
            return

        # save response to file
        self._export_save_file(jdata)


def main():
    app = ConfigData()
    if app.command == "export":
        app.export_file();
    elif app.command == "import":
        app.import_file();
    print("")


if __name__ == '__main__':
    main()
