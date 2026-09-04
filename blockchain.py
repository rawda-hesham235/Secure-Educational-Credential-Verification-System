import hashlib
import os
import pickle
import datetime
from cryptography.fernet import Fernet
import qrcode

def get_key():
    """
    Retrieve the encryption key from file if it exists.
    Otherwise, generate a new key and save it.
    """
    key_file ='key.key'
    if os.path.exists(key_file):
        with open(key_file,'rb') as f:
            key = f.read()
    else :
        key = Fernet.generate_key()
        with open (key_file,'wb') as f:
            f.write(key)
    return key

class Block:
    def __init__(self,index,timestamp,file_name,file_hash,previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.file_name = file_name
        self.file_hash = file_hash
        self.previous_hash = previous_hash
        self.hash=self.compute_hash()

    def compute_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.file_name}{self.file_hash}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain =[]
        self.fernet = Fernet(get_key())
        self.load_chain()
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_name="Genesis Block",
            file_hash="0",
            previous_hash="0" 
        )
        self.chain.append(genesis_block)
        self.save_chain()

    def add_block (self, file_name, file_data):
        file_hash=hashlib.sha256(file_data).hexdigest()
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_name=file_name,
            file_hash=file_hash,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()
        qr_file_name = f"block_{new_block.index}_qr.png"
        self.generate_qr_code(new_block.hash, qr_file_name)

        return new_block

    def generate_qr_code(self, data, file_name="qr_code.png"):
        """
        Generate a QR code for the given data and save it as an image.
        """
        output_dir = "qr_codes"
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, file_name)
        qr = qrcode.QRCode(
            version=1,  
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,  
            border=4,  
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(full_path)
        
    def check_file (self, file_data):
        file_hash = hashlib.sha256(file_data).hexdigest()
        for block in self.chain :
            if block.file_hash == file_hash :
                return block
        return None

    def delete_block(self,file_data):
        """
        Delete a block containing the file (based on its hash) from the chain,
        then rehash subsequent blocks. The genesis block cannot be deleted.
        Returns the index of the deleted block or None if not found.
        """
        file_hash=hashlib.sha256(file_data).hexdigest()
        index_to_delete = None
        for i ,block in enumerate(self.chain):
            if i !=0 and block.file_hash == file_hash:
                index_to_delete=i
                qr_file_path = os.path.join("qr_codes", f"block_{block.index}_qr.png")
                if os.path.exists(qr_file_path):
                    os.remove(qr_file_path)
                break

        if index_to_delete is None :
            return None

        del self.chain[index_to_delete]
        # Recompute indices and hashes for subsequent blocks.
        for i in range(index_to_delete, len(self.chain)):
            prev_hash=self.chain[i-1].hash if i > 0 else "0"
            self.chain[i].index = i
            self.chain[i].previous_hash = prev_hash
            self.chain[i].hash = self.chain[i].compute_hash()
        self.save_chain()
        return index_to_delete

    def get_all_files(self):
        """
        Return details of all blocks in the blockchain.
        """
        details = []
        for block in self.chain:
            details.append(
                f" Index: {block.index} \n "
                f"Timestamp: {block.timestamp} \n "
                f"File Name: {block.file_name} \n "
                f"File Hash: {block.file_hash}\n "
                f"Block Hash: {block.hash} \n "
                f"Previous Hash: {block.previous_hash} \n "
                "-----------------------------------------\n"
            )
        return details

    def reset_chain (self):
        """
        Delete all blocks and recreate the genesis block.
        """
        self.chain = []
        self.delete_all_qr_codes()
        self.create_genesis_block()
        
    def delete_all_qr_codes(self):
        qr_folder = "qr_codes"
        if os.path.exists(qr_folder):
            for file in os.listdir(qr_folder):
                if file.endswith(".png"):
                    os.remove(os.path.join(qr_folder, file))

    def save_chain(self):
         # Pickle the chain and encrypt it before saving.
        data = pickle.dumps(self.chain)
        encrypted_data = self.fernet.encrypt(data)
        with open ("blockchain.pkl","wb") as f:
            f.write(encrypted_data)
    
    def load_chain(self):
        if os.path.exists("blockchain.pkl"):
            with open ("blockchain.pkl","rb") as f:
                encrypted_data = f.read()
            try:
                data = self.fernet.decrypt(encrypted_data)
                self.chain = pickle.loads(data)
            except Exception as e:
                print("Error decrypting blockchain file:", e)
                self.chain = []
        else:
            self.chain = []

