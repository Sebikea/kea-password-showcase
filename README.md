# **Purpose**

## The purpose of this app is to demonstrate some of the differences in security by increasing password length, and choosing better suited hashing algorithms for password storage
## The speed of cracking will largely depend on the resources of the system running the app

# **Installation**

1. Clone the project and cd into folder
2. If you prefer, make a virtual environment
 ```
 python -m venv .venv
 source .venv/bin/activate
 ```
3. Install the python requirements
  ```
  pip install -r requirements.txt
  ```
4. Run the webapp
  ```
 python3 main.py
  ```

# **Prerequisites**
* There's a couple of paths that might need to be adjusted in main.py
* You need john and hashcat installed, and callable from terminal
* rockyou.txt is not included and needs to be placed in /wordlists (or some other wordlist that you prefer)


