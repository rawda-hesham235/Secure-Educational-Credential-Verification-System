import threading
import tkinter as tk
from tkinter import ttk
from blockchain import Blockchain
from gui import BlockchainApp
import web_app

def run_flask():
    # Run the Flask app without the reloader to avoid conflicts with threading.
    web_app.app.run(debug=True, port=4000 , use_reloader=False)

def main():
    # Create a single blockchain instance and share it with both the web app and GUI.
    blockchain = Blockchain()
    web_app.blockchain = blockchain


     # Start the Flask web server in a separate daemon thread.
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

     # Launch the Tkinter GUI.
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    app = BlockchainApp(root,blockchain)
    root.mainloop()

if __name__=="__main__":
    main()