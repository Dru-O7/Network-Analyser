const uploadForm = document.getElementById('uploadForm');
const tablesDiv = document.getElementById('tables');

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData();
    const pcapFileInput = document.getElementById('pcapFileInput');
    formData.append('pcapfile', pcapFileInput.files[0]);

    try {
        const response = await fetch('/upload-pcap', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const { csvData, images } = await response.json();

        csvData.forEach(csv => {
            const csvData = csv.data.split('\n');
            const headers = csvData[0].split(',');
            const rows = csvData.slice(1).map(row => row.split(','));

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

        // Display the images
        images.forEach(image => {
            const img = document.createElement('img');
            img.src = `graphs/${image}`;

            // Add image to the page
            tablesDiv.appendChild(img);
        });
    } catch (error) {
        console.error('Error:', error);
    }
});
