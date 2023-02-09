import pandas as pd
import tkinter as tk
import random as r
FONT = ("Javanese Text", 40, "normal")

class Flashcards(tk.Canvas):
    def __init__(self, width, height, master, path):
        super().__init__(width=width, height=height, master = master)
        self.config(bg="#B1DDC6", highlightthickness=0, bd = 0 )
        self.front_side = tk.PhotoImage(file='images/card_front.png')
        self.front = self.create_image(width/2, height/2, image=self.front_side)

        self.back_side = tk.PhotoImage(file='images/card_back.png')
        self.back = self.create_image(width/2, height/2, image=self.back_side)

        self.text = self.create_text(width/2, height/2, anchor="center", font=FONT)

        self.place(anchor='center', relx=0.5, rely=0.4)


        # Import word bank from .csv file
        self.path = path
        self.bank = pd.read_csv(self.path)

        # Add correct and incorrect columns
        for label in ("Correct", "Incorrect"):
            if label not in self.bank.columns:
                self.bank[label] = 0
            else:
                for row in self.bank.index:
                    if pd.isnull(self.bank.at[row, label]):
                        self.bank.at[row, label] = 0

        # Derive correct-incorrect ratio
        self.update()

        # Quick access attributes
        self.length = len(self.bank)
        self.current_index = None
        self.french = None
        self.english = None

        self.difficulty = .8
        self.proceed = True

    def update(self, correct=None):
        """Updates the correct-incorrect ratio"""
        # Tally correct/incorrect values
        if correct == False:
            self.bank.at[self.current_index, "Incorrect"] += 1
        elif correct == True:
            self.bank.at[self.current_index, "Correct"] += 1

        # Re-calculate ratio and sort dataframe
        self.bank['Ratio'] = self.bank.Correct / (self.bank.Correct + self.bank.Incorrect)
        self.bank.sort_values(by='Ratio', ascending=False, inplace=True, kind="mergesort")
        self.bank.reset_index(drop=True, inplace=True)

    def generate(self):
        self.proceed = False
        mean = len(self.bank)
        for row in range(len(self.bank) - 1, -1, -1):

            # Move reference position up until correct/incorrect ratio exceeds threshold
            if self.bank.at[row, 'Ratio'] < self.difficulty or pd.isnull(self.bank.at[row, 'Ratio']):
                mean -= 1

        # Generate random item around reference position (redraw if exceeds bound)
        self.current_index = int(r.normalvariate(mu=mean, sigma=20))
        while self.current_index < 0 or self.current_index > len(self.bank):
            self.current_index = int(r.normalvariate(mu=mean, sigma=20))

        # Modify display text
        self.french = self.bank.at[self.current_index, 'French']
        self.english = self.bank.at[self.current_index, 'English']


    def display(self):
        """Draw a random item from the word bank and display it"""
        self.tag_raise(self.front)
        self.itemconfig(self.text, text = self.french)
        self.tag_raise(self.text)
        self.after(ms=3000, func=self.flip)



    def flip(self):
        self.tag_raise(self.back)
        self.itemconfig(self.text, text=self.english)
        self.tag_raise(self.text)
        self.proceed = True
        return show_buttons()


    def draw_card(self):
        if self.proceed:
            self.generate()
            self.display()

    def export(self):
        self.bank.to_csv(self.path, index=False)
        print("Data Updated!")


def new_round(correct):
    my_cards.update(correct=correct)
    game_round()

def show_buttons():
    b_correct.place(anchor="center", relx=.7, rely=.8, height = 50, width = 50)
    b_wrong.place(anchor="center", relx=.3, rely=.8, height = 50, width = 50)

def hide_buttons():
    b_wrong.place_forget()
    b_correct.place_forget()

def game_round():
    hide_buttons()
    my_cards.draw_card()

def game_exit():
    my_cards.export()
    root.destroy()


root = tk.Tk()
root.title("Il Pomodoro")
root.config(bg="#B1DDC6")
# root.iconbitmap("my_icon.ico")
root.minsize(width=500, height=500)
root.maxsize(width=500, height=500)

img_correct = tk.PhotoImage(file="./images/right.png")
b_correct = tk.Button(command=lambda: new_round(correct=True), image = img_correct, highlightthickness=0, bd = 0, bg="#B1DDC6", activebackground="#B1DDC6")
img_wrong = tk.PhotoImage(file="./images/wrong.png")
b_wrong = tk.Button(command=lambda: new_round(correct=False), image=img_wrong, highlightthickness=0, bd = 0, bg="#B1DDC6", activebackground="#B1DDC6")


my_cards = Flashcards(400, 263, root, "data/french_words.csv")

game_round()

root.bind("<Escape>", lambda event: root.destroy())
root.protocol("WM_DELETE_WINDOW", game_exit)
root.mainloop()



