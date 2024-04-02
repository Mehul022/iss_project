const http = require('http');
const fs = require('fs');
const path = require('path'); // Module for working with file paths

const server = http.createServer((req, res) => {
    console.log('Request has been made from the browser to the server');

    // Parse the URL
    const url = req.url;
    console.log(req.url);
    let filePath = '.' + url;

    // If the request is for '/', serve index.html by default
    if (url === '/') {
        filePath = './index.html';
    }

    // Read the file from the file system
    fs.readFile(filePath, (err, fileData) => {
        if (err) {
            console.error(err);
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
        } else {
            // Determine the appropriate content type based on file extension
            const extname = path.extname(filePath);
            let contentType = 'text/html'; // Default content type
            switch (extname) {
                case '.js':
                    contentType = 'text/javascript';
                    break;
                case '.css':
                    contentType = 'text/css';
                    break;
                case '.json':
                    contentType = 'application/json';
                    break;
                case '.png':
                    contentType = 'image/png';
                    break;
                case '.jpg':
                    contentType = 'image/jpg';
                    break;
                case '.mp4':
                    contentType = 'video/mp4';
                    break;
            }

            // Set the appropriate content type header
            res.writeHead(200, { 'Content-Type': contentType });

            // Serve the file content
            res.end(fileData);
        }
    });
});

const PORT = 5001;
server.listen(PORT, 'localhost', () => {
    console.log(`Server running on port ${PORT}`);
});
