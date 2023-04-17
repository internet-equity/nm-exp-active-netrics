const express = require('express')
const {spawn} = require('child_process');
const http = require('http');
const PORT = 80;
const toml = require('toml');
const fs = require('fs');
const querystring = require('querystring');
const url = require('url');
toml_path = "../vca_automation/config.toml"
python_path = ""
var running = false;

function runBashScript(vca) {
	script = spawn('./run.sh', [vca]);
	script.on('close', (code) => {
		running = false;
		console.log(`child process exited with code ${code}`);
	});

	script.stdout.setEncoding("utf8")
	script.stderr.setEncoding("utf8")
	script.stdout.on('data', (data) => { console.log(data.toString())});
	script.stderr.on('data', (data) => { console.log(data.toString())});

}

const server = http.createServer(async (req, res) => {
    //set the request route
    const config = toml.parse(fs.readFileSync(toml_path, 'utf-8'));

    let parsedUrl = url.parse(req.url, true);
    let queryStr = querystring.parse(parsedUrl.query);
    if (parsedUrl.pathname === "/run-test" && req.method === "GET") {
       	if(running) {
	   res.writeHead(200, { 'Content-Type': 'application/json' });
	   res.write(JSON.stringify({'busy': true})); 
	   res.end();
       	} else {
	   running = true;
	   vca = parsedUrl.query['vca']
	   vcaUrl = config[vca]['url'];
	   res.writeHead(200, { 'Content-Type': 'application/json' });
	   res.write(JSON.stringify({'busy': false, 'url': vcaUrl})); 
	   res.end();
	   runBashScript(vca);
    	}
    }
    // If no route present
    else {
        res.writeHead(404, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ message: "Route not found" }));
    }
});

server.listen(PORT, function() {
    console.log(`Server listening on: http://localhost:${PORT}`);
})
