### 🌐 Network Analyzer

This web interface empowers users to upload PCAP files for analysis and visualize the results through CSV reports and captivating charts.

#### 📋 Requirements
- Python libraries (specified in `requirements.txt`)
- HTML, CSS, JavaScript
- Node.js (for server-side scripting)

#### 🚀 Usage
1. Ensure the necessary Python libraries are installed by running `pip install -r requirements.txt`.
2. Initiate the server by executing `node server.js`.
3. Access the web interface at [http://localhost:3000](http://localhost:3000).

#### 🛠️ Functionality
- Users can effortlessly upload PCAP files using the provided form.
- Upon file selection, the filename is prominently displayed.
- After submission, the Python script analyzes the PCAP file.
- Results, including CSV reports and visually appealing charts, are dynamically presented.
- CSV reports comprise:
  - Protocol distribution
  - Top IP address communications
  - Share of each protocol between IPs
  - DNS requests
- Visualizations include:
  - Distribution of protocols (pie chart)
  - Share of each protocol between IPs (stacked bar chart)

#### 📂 Files
- `main.py`: Python script for PCAP file analysis.
- `server.js`: Node.js server for file uploads and script execution.
- `index.html`: HTML file for the user interface.
- `styles.css`: CSS file for enhanced styling.
- `script.js`: JavaScript file for interactive features.

#### 📹 Demo and Installation
Experience the demo and installation process on [YouTube](https://youtu.be/3ZLSvOzc9ns).
