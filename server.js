const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/')
    },
    filename: (req, file, cb) => {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname))
    }
});
const upload = multer({ storage: storage });

// Serve static files from 'public' and 'graphs' directories
app.use(express.static('public'));
app.use(express.static('graphs'));

// Endpoint to handle file upload and script execution
app.post('/upload-pcap', upload.single('pcapfile'), (req, res) => {
    const filePath = req.file.path;
    const fileName = req.file.originalname; // Get the original filename
    const command = 'python';
    const args = ['main.py', filePath, 'protocol_distribution.csv', 'top_ip_communications.csv', 'share_of_protocol_between_ips.csv']; // Specify the output CSV files

    execFile(command, args, { maxBuffer: 1024 * 500 }, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).send(`Error executing script: ${error}`);
        }

        // Read the generated CSV files
        const files = ['protocol_distribution.csv', 'top_ip_communications.csv', 'share_of_protocol_between_ips.csv'];
        const csvData = [];

        for (const file of files) {
            const data = fs.readFileSync(file, 'utf8');
            csvData.push({ filename: file, data });
        }

        // Check if a file has been uploaded before
        const isFileUploaded = !!req.file;

        // Send the CSV filenames and file upload status to the client
        res.json({ csvData, fileName, isFileUploaded });
    });
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});

// Directory for file uploads
const uploadDir = 'uploads/';
if (!fs.existsSync(uploadDir)){
    fs.mkdirSync(uploadDir);
}
