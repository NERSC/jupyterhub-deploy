var http = require('http') 
// var log = require('winston');

var program_name = process.argv[0]; //value will be "node"
var script_path = process.argv[1]; //value will be "yourscript.js"
var redirect_url = process.argv[2]; //value will be "arg"

if (!redirect_url) {
    redirect_url = "https://localhost/";
}

// parse url ... cannot be relative otherwise we just keep redirecting back to ourselves





// log.remove(log.transports.Console);
// log.add(log.transports.Console, {
//     colorize: (process.stdout.isTTY && process.stderr.isTTY),
//     level: "debug",
//     timestamp: function () {
//       return strftime("%H:%M:%S.%L", new Date());
//     },
//     label: 'redirect.js',
// });

var server = http.createServer(function(req, res) {
    // Log request -> redirect
    console.log("302 Redirect " + req.headers.host + " -> " + redirect_url)

    res.writeHead(302, {
        'Location': redirect_url
    });
    res.end();
});

server.listen(80)