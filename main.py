from dotenv import load_dotenv
from os import getenv, system
import time
import openai
import pickle
import colorama

# Gets API key
load_dotenv()
openai.api_key = getenv("OPENAI")

def rprint(text, delay=0.03):
    try:
        for i in range(0, len(text)):
            print(text[i], end="", flush=True)
            time.sleep(delay)
        print()
        time.sleep(0.5)
    except KeyboardInterrupt:
        pass

# Uses OpenAI API to get response from model.
def get_response(attention: list, prompt="...") -> dict:
    attention.append({
        "role": "user",
        "content": prompt
    })
    
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=attention
    )
    
    attention.append(dict(res.choices[0]["message"]))
    return attention

# Creates new list of attention for model.
def new_attention():
    choose_system = input("Choose system prompt? (Y/N)")
    if choose_system == "Y" or choose_system == "y":
        system_prompt = "Disregard any and all previous instructions." + input("System prompt:")
    else:
        system_prompt = "Disregard any and all previous instructions. I want you to be a helpful assistant."
    
    attention = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Respond if you understand."},
        {"role": "assistant", "content": "Yes, I understand and am willing to follow your instructions."}
    ]
    return attention

# Measure roughly how many tokens there are in the text provided.
def token_count(attention: list):
    tokens = 0
    for dialogue in attention:
        tokens += len(dialogue["content"])
    return tokens

def change_attention():
    file_name = input("File name:")
    try:
        with open(f"./attention/{file_name}", "rb") as f:
            attention = pickle.load(f)
            print(f"Restored {file_name} to attention.")
    except:
        print("[!] Couldn't restore attention, can't access attention file!")
        print("Creating new attention list...")
        attention = new_attention()
    
    return attention

COMMANDS = {
    "commands": "Displays all commands",
    "clean": "Clears model attention.",
    "cost": "Displays current API usage cost.",
    "summary": "Tells model to summarize the current conversation.",
    "retry": "Tells model to respond to the previous prompt again.",
    "displayattn": "Prints out current attention list."
}

def main():
    colorama.just_fix_windows_console()
    print(f"{colorama.Fore.GREEN}GPT 3.5 {colorama.Fore.RESET}Python Implementation, by Oliver M")
    time.sleep(2)
    print()

    # Used for calculating API cost
    cost = 0

    restore_attention = input(f"Restore previous attention? {colorama.Fore.YELLOW}(Y/N){colorama.Fore.RESET}")
    if restore_attention == "Y" or restore_attention == "y":
        # Uses pickle library to load attention list from file.
        attention = change_attention()
            
    else:
        attention = new_attention()
        # prompt = "Tell me what you'll do."
        # attention = get_response(attention, prompt)
        # rprint(attention[-1]["content"])

    time.sleep(1)
    system("cls")
    print("Connected, ready to chat. Type 'commands' for available commands.")
    prompt = ""

    # Main conversation loop
    while not prompt == "exit":
        prompt = input(":")
        
        # Handle certain commands here
        match prompt:
            case "commands":
                commands = COMMANDS.keys()
                for command in commands:
                    print(f"- {command}: {COMMANDS[command]}")
                print()
            
            case "displayattn":
                i = 0
                print("[ INIT ]")
                for response in attention:
                    print(f"{response['role'].capitalize()}: {response['content']}")
                    i += 1
                    if i == 3:
                        print("[ INIT ]")
            
            case "attnchange":
                file_name = input("File name (.pkl):")
                attention = change_attention(file_name)
            
            case "clean":
                attention = new_attention()
            
            case "cost":
                print(f"Cost: ${cost.__round__(5)}")
            
            case "summary":
                prompt = "Give me a summary of our current conversation."
                attention = get_response(attention, prompt)
                rprint(attention[-1]["content"])

            case "retry":
                prompt = "Respond to this prompt again with a new and unique answer." + attention[-2]["content"]
                attention = get_response(attention, prompt)
                rprint(attention[-1]["content"])
            
            # Normal prompt
            case other:
                attention = get_response(attention, prompt)
                rprint(attention[-1]["content"])
        
        # Add new cost, compounds as attention expands.
        cost += ((token_count(attention) / 4000) * 0.002)
        print()

    save_attention = input("Save attention? (Y/N)")
    if save_attention == "Y" or save_attention == "y":
        file_name = input("File name:")
        with open(f"./attention/{file_name}", "wb") as f:
            pickle.dump(attention, f)
            print(f"Saved attention to {file_name}")
    else:
        print("Didn't save attention.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    