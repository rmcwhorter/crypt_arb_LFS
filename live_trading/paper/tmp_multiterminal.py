import tkinter as tk

def newwindow():

    def sign_done():
        david = user.get()
        javed = pword.get()
        tk.Label(newwindow, text=david).pack()
        tk.Label(newwindow, text=javed).pack()

    newwindow = tk.Toplevel()
    newwindow.title('Sign Up')
    newwindow.geometry('200x400')

    user = tk.Entry(newwindow)
    user.pack()
    pword = tk.Entry(newwindow)
    pword.pack()

    tk.Button(newwindow, text='done now', command=sign_done).pack()


root = tk.Tk()
root.title('Gulmeena')
root.geometry("500x200")

tk.Button(root, text='Go', command=newwindow).pack()

root.mainloop()