const http = require('http');
const fs = require('fs');
const path = require('path');
const mysql = require('mysql'); // Import the MySQL package

// Create a MySQL connection
const mysqlConnection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'Paarth123#',
    database: 'ISSPROJECT'
});

mysqlConnection.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL database:', err);
        return;
    }
    console.log('Connected to MySQL database');
});

const server = http.createServer((req, res) => {
    console.log('Request has been made from the browser to the server');

    if (req.method === 'POST' && req.url === '/signup') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString(); // Accumulate request body data
        });
        req.on('end', () => {
            // Parse form data
            const formData = new URLSearchParams(body);
            const username = formData.get('username');
            const email = formData.get('email');
            const password = formData.get('password');
            
            // Now you can use the username, email, and password as needed,
            // for example, save them to your MySQL database
            mysqlConnection.query('INSERT INTO users (id,username, email, password) VALUES (1,?, ?, ?)', [username, email, password], (err, results) => {
                if (err) {
                    console.error('Error saving data to database:', err);
                    res.writeHead(500, { 'Content-Type': 'text/plain' });
                    res.end('Internal Server Error');
                } else {
                    console.log('Data saved to database');
                    res.writeHead(200, { 'Content-Type': 'text/plain' });
                    res.end('Sign-up successful!');
                }
            });
        });
    } else {
        // Your existing code for serving files
        const url = req.url;
        console.log(req.url);
        let filePath = '.' + url;

        if (url === '/') {
            filePath = './index.html';
        }

        fs.readFile(filePath, (err, fileData) => {
            if (err) {
                console.error(err);
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end('404 Not Found');
            } else {
                const extname = path.extname(filePath);
                let contentType = 'text/html';
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

                res.writeHead(200, { 'Content-Type': contentType });
                res.end(fileData);
            }
        });
    }
});

const PORT = 5500;
server.listen(PORT, 'localhost', () => {
    console.log(`Server running on port ${PORT}`);
});
