var build_client = function(host, version) {
    if (version == undefined) {
        version = '0';
    }

    var theClient = function(host, version) {
        this._host = host;
        this._version = version;
    };
    
    new Request.JSON({
        url: host + '/_api_list/?version=' + version, 
        method: 'get',
        onSuccess: function(data) {
            data.forEach( function(obj) {
                var method = obj[0];
                var path = obj[1];
                var data = obj[2];
                
                var p = path.split('/').slice(1).join('_');
                
                if (p[p.length-1] == '_') {
                    p = p.substring(0, p.length-1);
                }

                theClient.prototype[p] = function(d, cb) {
                    if (typeof d == 'function') {
                        cb = d;
                        d = {};
                    }
                    var return_data = undefined;
                    var url = host + '/' + path;
                    var args = {
                        url: url, 
                        method: ""+method,
                        onSuccess: function(data) {
                            return_data = data;
                        },
                        data:d
                        }
                    
                    if (cb == undefined) {
                        args['async'] = false;
                    } else {
                        args['async'] = true;
                        args['onSuccess'] = function(data) {
                            cb(data);
                        }
                    }
                    new Request.JSON(args).send();
                    return return_data;
                }
            });
        },
        async: false
        }).send();
    
    return new theClient(host, version);
}

