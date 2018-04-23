import abc
import pdb
import copy
from utils import *
from diff_base import DiffBase
from pdb import Pdb

class DiffDatastorages(DiffBase):
    def __init__(self, jtbuf, cache2file = True, require_initdata=False):
        ''' init parent '''
        self.inst_name = "datastorages"        
        super(DiffDatastorages, self).__init__(self.inst_name, jtbuf, cache2file,False)
  
    def __path_sanity_check(self, keys):
        ''' verify request path '''
        if (not len(keys) in(7,8) or not keys[5] in {"cluster", "server"}):
            return False
        if (len(keys) == 7 and keys[5] != "cluster"):
            return False
        if (len(keys) == 8 and keys[5] != "server"):
            return False
        if (keys[3] != self.inst_name):
            return False
        return True
    
    def _analyze_data(self, jdata):
        values = {}
        print jdata
        for it in jdata:
            #basic type check 
            if not type(it) is type({}):
                Debug.error("Bad input datastorages data type: %s" % str(type(it)))
                continue 
            
            # prefix check
            key = it["Key"]
            # prefix need modify''
            if not key.startswith("cm/values/"):  
                Debug.error("Bad input prefix: %s" % key)
                continue;
                
            #  "cm/values/{version}/datastorages/datastorage{i}/server/{host}/key{i}/"
            #    0  1       2       3            4              5        6    7    
            #  "cm/values/{version}/datastorages/datastorage{i}/cluster/key{i}/"
            #    0  1       2       3            4              5       6       
            keys = key.split("/");
            
            # basic path check
            #  "cm/values/{version}/datastorages" :clear all datastorages keys
            if len(keys)==4:
                continue
                
            if not self.__path_sanity_check(keys):
                Debug.error("Bad input key: %s, %s" % (key, str(keys)))
                continue

            # make component name and parameter
            datastorage = keys[4]
            parameter   = keys[6];
            if (keys[5] == "server"):
                # parameter is not for this host!!!, ignore
                parameter = keys[7]
                if get_hostname() != keys[6]:
                    continue;
                

            # decode base64 encoded value
            value = it["Value"]
            if (value and '' != value):
                value = base64decode(value)

            # append parameter values
            jobj = {"Value": value,
                    "ModifyIndex": it["ModifyIndex"]};
            if (datastorage in values.keys()):
                values[datastorage][parameter] = jobj;
            else:
                values[datastorage] = {parameter: jobj}

        values = {"Type": self.inst_name, "Value": values}
        return values


  
    def _add_single(self,add_values,ds_key,key_para,para_val,_command):
        if(not add_values.has_key(ds_key)):
            add_values[ds_key]={}
        if(not add_values[ds_key].has_key(key_para)):
            add_values[ds_key][key_para]=copy.deepcopy(para_val)
        '''else:    
            if (key_para.has_key('Command') and key_para['Command']=='add'):
                _command='add'''
        add_values[ds_key][key_para]['Command']=_command;   
        return add_values; 
    
    def _calculate_diff(self, new_data):
        ''' calculate_diff for datastorages
            The input format is the output of _analyze_data().
            The returned data format is same to input.
             The returned data format:
            {
                "Type": "datastorages",
                "Value": {          
                    "BASSP_MS": {                               # datastorages Name
                        "d1source": {                # Parameter key 
                            "ModifyIndex": 556,                 # ModifyIndex
                            "Value": "nnn"      # Value
                            "Command": update/remove/removeall
                        }, 
                        {                               # datastorages Name
                        "d2source": {                # Parameter key 
                            "ModifyIndex": 556,                 # ModifyIndex
                            "Value": "nnn"      # Value
                            "Command": update/remove/removeall
                        },...
                    }, ...
                }
            }
        '''
        print new_data
        jdata = new_data["Value"]
        jcache = self.watch_cache["Value"]

        ##Delete Command
        delete_all={}
        delete_values={}
        
        for cache_key,cache_val in jcache.items():      #foreach datastorages name
            if not cache_key in jdata.keys():
                Debug.notice("Diff detect delete multi: %s" %(cache_key))
                delete_all[cache_key]={}
                ''' construct remove all data'''
                delete_all[cache_key][cache_key]={}
                delete_all[cache_key][cache_key]["ModifyIndex"]=None
                delete_all[cache_key][cache_key]["Value"]=None
                delete_all[cache_key][cache_key]["Command"]='REMOVEALL'
            else:
                for ds_key,ds_val in cache_val.items():
                    if(not jdata[cache_key].has_key(ds_key)):   
                        if(not delete_values.has_key(cache_key)):
                            delete_values[cache_key]={}
                        if(not delete_values[cache_key].has_key(ds_key)):
                            Debug.notice("Diff detect delete single: %s" %(cache_key))
                            delete_values[cache_key][ds_key]=copy.deepcopy(ds_val)    
                            delete_values[cache_key][ds_key]['Command']='REMOVE'

        
        for del_key,del_val in delete_values.items():
            for ds_key,ds_val in delete_values[del_key].items():
                del jcache[del_key][ds_key]
            if (len(jcache[del_key])==0):
                del jcache[del_key]

        for del_key,del_val in delete_all.items():
            if len(jcache[del_key])==1:             #just one key then delete remove
                delete_values[del_key]=copy.deepcopy(jcache[del_key])
                for jc_key,jc_val in jcache[del_key].items():
                    delete_values[del_key][jc_key]['Command']='REMOVE'
                del jcache[del_key]    
            else:    
                delete_values[del_key]=copy.deepcopy(del_val)
                del jcache[del_key]
        # foreach component add or update
        
        add_values={}
        
        for comp_key, comp_val in jdata.items():        #foreach datastorages name
            # Warning: component not exists in jcache, add it.
            if not comp_key in jcache.keys():           #not exist detect add
                Debug.notice("Diff detect add multi: %s"%(comp_key))
                jcache[comp_key]=copy.deepcopy(comp_val);
                add_values[comp_key]=copy.deepcopy(comp_val);
                for ds_key in add_values[comp_key].keys():
                    #add_values[comp_key]['Command']='add'
                    add_values[comp_key][ds_key]['Command']='UPDATE'
                continue
                
            # foreach parameter
            for param_key, param_val in comp_val.items():    #foreach key 
                # Warning: parameter not exists in component, add it.
                # This shall for datasttorages[i]/keys[i],
                # or other case: such as add new datastorages[i].          
                if not param_key in jcache[comp_key].keys():
                    Debug.notice("Diff detect add single: %s"%(comp_key));
                    jcache[comp_key][param_key]= copy.deepcopy(param_val);
                    add_values=self._add_single(add_values, comp_key, param_key, param_val, 'UPDATE')
                                
                else:
                    Debug.notice("Diff detect update single: %s" %(comp_key))
                    if ((param_val["ModifyIndex"] != jcache[comp_key][param_key]["ModifyIndex"]) 
                        and (type(param_val["Value"]) != type(jcache[comp_key][param_key]["Value"])
                         or (param_val["Value"] != jcache[comp_key][param_key]["Value"]))
                        ):
                       jcache[comp_key][param_key]["Value"]= param_val['Value']
                       jcache[comp_key][param_key]["ModifyIndex"]= param_val['ModifyIndex']
                       add_values=self._add_single(add_values, comp_key, param_key, param_val, 'UPDATE')
                       
        for ds_key,ds_val in delete_values.items():
              if  not ds_key in add_values.keys():
                  if len(ds_val)==0:
                      add_values[ds_key]={}
                  else:
                      add_values[ds_key]=copy.deepcopy(ds_val)
              else:
                  for key,key_val in ds_val.items():
                      if not key in add_values[ds_key].keys():
                          add_values[ds_key][key]=copy.deepcopy(key_val)
                      else:
                          add_values[ds_key][key]=copy.deepcopy(key_val)    
        values = {"Type": self.inst_name, "Value": add_values}

        return values
       
