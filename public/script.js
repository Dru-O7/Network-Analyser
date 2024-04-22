const uploadForm = document.getElementById('uploadForm');
const pcapFileInput = document.getElementById('pcapFileInput');
const tablesDiv = document.getElementById('tables'); 

// Check if file is already uploaded
pcapFileInput.addEventListener('change', () => {
    if (pcapFileInput.files.length > 0) {
        pcapFileInput.style.backgroundColor = 'green';
        // Display the name of the uploaded file
        const fileNameDisplay = document.createElement('p');
        fileNameDisplay.textContent = `Uploaded file: ${pcapFileInput.files[0].name}`;
        uploadForm.appendChild(fileNameDisplay);
    }
});

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append('pcapfile', pcapFileInput.files[0]);

    try {
        const response = await fetch('/upload-pcap', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        const csvData = result.csvData || [];
        const images = result.images || [];

        // Process CSV data if available
        if (csvData.length > 0) {
            // Clear previous tables
            tablesDiv.innerHTML = '';
            csvData.forEach(csv => {
                const csvRows = csv.data.split('\n');
                const headers = csvRows[0].split(',');
                const rows = csvRows.slice(1).map(row => row.split(','));

                const table = document.createElement('table');
                const thead = document.createElement('thead');
                const tbody = document.createElement('tbody');

                // Hardcoded table headings
                const headingRow = document.createElement('tr');
                const headingCell = document.createElement('th');
                let headingText;

                if (csv.filename === 'protocol_distribution.csv') {
                    headingText = 'Protocol Distribution';
                } else if (csv.filename === 'top_ip_communications.csv') {
                    headingText = 'Top IP Address Communications';
                } else if (csv.filename === 'share_of_protocol_between_ips.csv') {
                    headingText = 'Share of each protocol between IPs';
                } else {
                    headingText = 'Unknown';
                }

                headingCell.textContent = headingText;
                headingCell.setAttribute('colspan', headers.length);
                headingRow.appendChild(headingCell);
                thead.appendChild(headingRow);

                // Create table header
                const headerRow = document.createElement('tr');
                headers.forEach(header => {
                    const th = document.createElement('th');
                    th.textContent = header;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);

                // Create table rows
                rows.forEach(rowData => {
                    const tr = document.createElement('tr');
                    rowData.forEach(cellData => {
                        const td = document.createElement('td');
                        td.textContent = cellData;
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });

                table.appendChild(thead);
                table.appendChild(tbody);
                tablesDiv.appendChild(table); 
            });
        }

        // Display images if available
        if (images.length > 0) {
            images.forEach(image => {
                const img = document.createElement('img');
                img.src = `graphs/${image}`;
                tablesDiv.appendChild(img); 
            });
        }

    } catch (error) {
        console.error('Error:', error);
    }
});
