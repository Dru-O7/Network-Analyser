### Network Analyzer

This web interface allows users to upload PCAP files for analysis and view the results in the form of CSV reports and visualizations.

#### Requirements
- Python libraries (specified in `requirements.txt`)
- HTML, CSS, JavaScript
- Node.js (for server-side scripting)

#### Usage
1. Ensure the required Python libraries are installed by running `pip install -r requirements.txt`.
2. Start the server by running `node server.js`.
3. Access the web interface at `http://localhost:3000`.

#### Functionality
- Users can upload a PCAP file using the provided form.
- Upon file selection, the filename is displayed.
- After submission, the PCAP file is analyzed by the Python script.
- Analysis results, including CSV reports and visualizations, are displayed on the web page.
- CSV reports include:
  - Protocol distribution
  - Top IP address communications
  - Share of each protocol between IPs
  - DNS requests
- Visualizations include:
  - Distribution of protocols (pie chart)
  - Share of each protocol between IPs (stacked bar chart)

#### Files
- `main.py`: Python script for analyzing PCAP files.
- `server.js`: Node.js server for handling file uploads and script execution.
- `index.html`: HTML file for the web interface.
- `styles.css`: CSS file for styling the web interface.
- `script.js`: JavaScript file for client-side scripting.

#### Demo and Installation
Watch the demo and installation on [YouTube](https://youtu.be/3ZLSvOzc9ns).
