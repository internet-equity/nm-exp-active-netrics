const {spawn} = require('child_process')


var running = false;

function runBashScript(vca) {
	script = spawn('./run.sh', [vca,'> server.log 2>&1']);
	script.on('close', (code) => {
		running = false;
		console.log(`child process exited with code ${code}`);
	});
	script.stdout.setEncoding('utf8')
	script.stderr.setEncoding('utf8')
	script.stdout.on('data', function(data) { console.log(data) });
	script.stderr.on('data', function(data) { console.log("error", data) })
}

runBashScript("teams")
