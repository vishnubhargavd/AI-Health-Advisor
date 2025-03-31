import google.generativeai as genai
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import math

# Configure your API key
try:
    genai.configure(api_key="api_key")  # Replace with your actual API key
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite')
except Exception as e:
    print(f"Error configuring API: {e}")
    model = None

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1="#3a7bd5", color2="#00d2ff", **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        for i in range(height):
            r = int((i/height)*255)
            g = int((i/height)*255)
            b = 255
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

class LoadingAnimation(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg='#2c3e50', highlightthickness=0)
        self.width = 50
        self.height = 50
        self.arc = self.create_arc(10, 10, 40, 40, start=0, 
                                 extent=120, outline='#ffffff', width=3)
        self.angle = 0
        self.animation_running = False

    def start_animation(self):
        self.animation_running = True
        self.rotate()

    def stop_animation(self):
        self.animation_running = False

    def rotate(self):
        if self.animation_running:
            self.angle += 12
            self.itemconfig(self.arc, start=self.angle)
            self.after(50, self.rotate)

class HealthAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Health Advisor")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Main gradient background
        self.gradient_bg = GradientFrame(root, color1="#3a7bd5", color2="#00d2ff")
        self.gradient_bg.pack(fill="both", expand=True)
        
        # Main container
        self.main_container = ttk.Frame(self.gradient_bg)
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", width=950, height=750)
        
        self.setup_ui()
        self.loading_animations = []

    def animate_header(self):
        colors = ['#ffffff', '#e0e0e0', '#c0c0c0', '#a0a0a0']
        def cycle_colors(index=0):
            self.header_label.config(foreground=colors[index % len(colors)])
            self.root.after(2000, cycle_colors, index + 1)
        cycle_colors()

    def get_diet_recommendation(self, personal_data):
        prompt = f"""
        Provide a professional diet recommendation with the following format:

        **Daily Calorie Intake:**
        * [specific calorie range] calories per day
        
        **Macronutrient Breakdown:**
        * Protein: [range] grams ([explanation])
        * Fat: [range] grams ([explanation])
        * Carbohydrates: [range] grams ([explanation])
        
        **Meal Plan Examples:**
        * Breakfast: [example 1], [example 2]
        * Lunch: [example 1], [example 2] 
        * Dinner: [example 1], [example 2]
        * Snacks: [example 1], [example 2]
        
        **Hydration:**
        * [specific recommendation] liters per day
        
        **Supplement Suggestions:**
        * [supplement 1]: [reason]
        * [supplement 2]: [reason]
        
        **Additional Notes:**
        * [important note 1]
        * [important note 2]

        Base this on:
        Age: {personal_data.get('age')}
        Gender: {personal_data.get('gender')}
        Weight: {personal_data.get('weight')} kg
        Height: {personal_data.get('height')} cm
        Activity Level: {personal_data.get('activity_level')}
        Dietary Restrictions: {personal_data.get('dietary_restrictions')}
        Goals: {personal_data.get('goals')}
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating diet recommendation: {e}"

    def get_posture_correction_advice(self, posture_data):
        prompt = f"""
        Provide professional posture advice with the following format:

        **Recommended Exercises:**
        * [exercise 1]: [description]
        * [exercise 2]: [description]
        
        **Ergonomic Adjustments:**
        * [adjustment 1]
        * [adjustment 2]
        
        **Frequency:**
        * [recommended frequency]
        
        **Warning Signs:**
        * [sign 1]
        * [sign 2]
        
        **When to Seek Help:**
        * [situation 1]
        * [situation 2]

        Base this on:
        Posture Issues: {posture_data.get('issues')}
        Duration: {posture_data.get('duration')}
        Pain Location: {posture_data.get('pain_location')}
        Work Environment: {posture_data.get('work_environment')}
        """
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating posture advice: {e}"

    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#2c3e50'
        fg_color = '#ffffff'
        accent_color = '#3498db'
        entry_bg = '#ecf0f1'
        text_bg = '#34495e'
        
        style.configure('.', background=bg_color, foreground='black', font=('Helvetica', 11))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Helvetica', 11))
        style.configure('TButton', background=accent_color, foreground='black', font=('Helvetica', 11, 'bold'))
        style.configure('TEntry', fieldbackground=entry_bg, foreground='black')
        style.configure('TCombobox', fieldbackground=entry_bg, foreground='black')
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', background='#34495e', foreground=fg_color, padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', accent_color)])
        style.configure('Header.TFrame', background='#34495e')
        style.configure('Accent.TButton', font=('Helvetica', 12, 'bold'),
                      foreground='black', background=accent_color,
                      padding=10, borderwidth=0)
        style.map('Accent.TButton',
                 background=[('active', '#2980b9'), ('pressed', '#1a5276')])

        # Header
        header = ttk.Frame(self.main_container, style='Header.TFrame')
        header.pack(fill='x', pady=(0, 10))
        
        self.header_label = ttk.Label(header, 
                                    text="AI Health Advisor", 
                                    font=('Helvetica', 20, 'bold'), 
                                    foreground=fg_color)
        self.header_label.pack(pady=15)
        self.animate_header()

        # Notebook for sections
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Input Section
        input_frame = ttk.Frame(self.notebook)
        self.setup_inputs(input_frame)
        self.notebook.add(input_frame, text="Input Parameters")

        # Results Section
        results_frame = ttk.Frame(self.notebook)
        self.setup_results(results_frame)
        self.notebook.add(results_frame, text="Recommendations")

        # Loading overlay
        self.loading_overlay = tk.Canvas(self.main_container, highlightthickness=0, bg=bg_color)
        self.loading_label = ttk.Label(self.loading_overlay, 
                                     text="Analyzing your health data...", 
                                     font=('Helvetica', 14), 
                                     background=bg_color,
                                     foreground=fg_color)
        self.loading_animation = LoadingAnimation(self.loading_overlay, width=80, height=80)

    def setup_inputs(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Personal Info
        personal_frame = ttk.LabelFrame(container, text="Personal Information", 
                                      padding=(10, 5))
        personal_frame.pack(fill='x', pady=5)
        
        fields = [
            ("Age:", "age_entry", "number"),
            ("Gender:", "gender_var", "option", ["Male", "Female", "Other"]),
            ("Weight (kg):", "weight_entry", "number"),
            ("Height (cm):", "height_entry", "number"),
            ("Activity Level:", "activity_var", "option", 
             ["Sedentary", "Light", "Moderate", "Active", "Very Active"]),
            ("Dietary Restrictions:", "restrictions_var", "option", 
             ["None", "Vegetarian", "Vegan", "Gluten-free", "Dairy-free", "Other"]),
            ("Goals:", "goals_var", "option", 
             ["Weight loss", "Muscle gain", "General health", "Improved fitness", "Other"])
        ]

        for i, (label, var, typ, *rest) in enumerate(fields):
            row = ttk.Frame(personal_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label, width=20, anchor='e').pack(side='left', padx=5)
            if typ == "option":
                setattr(self, var, tk.StringVar(value=rest[0][0]))
                cb = ttk.Combobox(row, textvariable=getattr(self, var), 
                                 values=rest[0], state='readonly')
                cb.pack(side='left', fill='x', expand=True, padx=5)
            else:
                entry = ttk.Entry(row)
                entry.pack(side='left', fill='x', expand=True, padx=5)
                setattr(self, var, entry)

        # Posture Info
        posture_frame = ttk.LabelFrame(container, text="Posture Information", 
                                     padding=(10, 5))
        posture_frame.pack(fill='x', pady=5)
        
        posture_fields = [
            ("Posture Issues:", "issues_entry", "text"),
            ("Duration:", "duration_entry", "text"),
            ("Pain Location:", "pain_entry", "text"),
            ("Work Environment:", "work_var", "option", 
             ["Office Desk Job", "Remote Work", "Manual Labor", "Healthcare", "Education", "Other"])
        ]

        for i, (label, var, typ, *rest) in enumerate(posture_fields):
            row = ttk.Frame(posture_frame)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label, width=20, anchor='e').pack(side='left', padx=5)
            if typ == "option":
                setattr(self, var, tk.StringVar(value=rest[0][0]))
                cb = ttk.Combobox(row, textvariable=getattr(self, var), 
                                 values=rest[0], state='readonly')
                cb.pack(side='left', fill='x', expand=True, padx=5)
            else:
                entry = ttk.Entry(row)
                entry.pack(side='left', fill='x', expand=True, padx=5)
                setattr(self, var, entry)

        # Generate Button
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill='x', pady=(15, 5))
        
        self.generate_btn = tk.Button(btn_frame, 
                                    text="GENERATE RECOMMENDATIONS", 
                                    command=self.start_processing,
                                    font=('Helvetica', 12, 'bold'),
                                    bg='#3498db',
                                    fg='black',
                                    activebackground='#2980b9',
                                    activeforeground='black',
                                    relief='raised',
                                    borderwidth=0,
                                    padx=20,
                                    pady=12)
        self.generate_btn.pack(fill='x', expand=True)

    def setup_results(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Diet Recommendations
        diet_frame = ttk.LabelFrame(container, text="Diet Recommendations")
        diet_frame.pack(fill='both', expand=True, pady=5)
        self.diet_text = scrolledtext.ScrolledText(diet_frame, wrap=tk.WORD, 
                                                 font=('Helvetica', 12), 
                                                 padx=10, pady=10,
                                                 bg='#ecf0f1', fg='black',
                                                 insertbackground='black',
                                                 relief='flat')
        self.diet_text.pack(fill='both', expand=True)

        # Posture Recommendations
        posture_frame = ttk.LabelFrame(container, text="Posture Recommendations")
        posture_frame.pack(fill='both', expand=True, pady=5)
        self.posture_text = scrolledtext.ScrolledText(posture_frame, wrap=tk.WORD, 
                                                    font=('Helvetica', 12), 
                                                    padx=10, pady=10,
                                                    bg='#ecf0f1', fg='black',
                                                    insertbackground='black',
                                                    relief='flat')
        self.posture_text.pack(fill='both', expand=True)

        # Configure text widget tags
        for widget in [self.diet_text, self.posture_text]:
            widget.tag_configure("bold", font=('Helvetica', 12, 'bold'), foreground='black')
            widget.tag_configure("bullet", lmargin1=20, lmargin2=40, 
                               font=('Helvetica', 12), foreground='black')

    def insert_formatted_text(self, widget, text):
        widget.config(state='normal')
        widget.delete(1.0, tk.END)
        
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith('**') and line.strip().endswith('**'):
                clean_line = line.strip('* \n')
                widget.insert(tk.END, clean_line + '\n', 'bold')
            elif line.strip().startswith('*'):
                clean_line = '• ' + line.strip('* \n')
                widget.insert(tk.END, clean_line + '\n', 'bullet')
            else:
                widget.insert(tk.END, line + '\n')
        
        widget.config(state='disabled')

    def start_processing(self):
        self.show_loading(True)
        self.generate_btn.config(state='disabled')
        threading.Thread(target=self.process_data, daemon=True).start()

    def process_data(self):
        try:
            personal_data = self.get_personal_data()
            posture_data = self.get_posture_data()
            
            diet_rec = self.get_diet_recommendation(personal_data)
            posture_rec = self.get_posture_correction_advice(posture_data)
            
            self.root.after(0, self.show_results, diet_rec, posture_rec)
        except Exception as e:
            error_msg = f"Error processing data: {str(e)}"
            self.root.after(0, self.show_results, error_msg, error_msg)
        finally:
            self.root.after(0, self.show_loading, False)

    def show_loading(self, show):
        if show:
            self.loading_overlay.place(x=0, y=0, relwidth=1, relheight=1)
            self.loading_animation.place(relx=0.5, rely=0.4, anchor='center')
            self.loading_label.place(relx=0.5, rely=0.5, anchor='center')
            self.loading_animation.start_animation()
        else:
            self.loading_animation.stop_animation()
            self.loading_overlay.place_forget()
            self.generate_btn.config(state='normal')

    def show_results(self, diet, posture):
        self.insert_formatted_text(self.diet_text, diet)
        self.insert_formatted_text(self.posture_text, posture)
        self.notebook.select(1)  # Switch to results tab
        self.animate_results()

    def animate_results(self):
        for widget in [self.diet_text, self.posture_text]:
            widget.config(state='normal')
            widget.tag_configure("highlight", background="#d6eaf8")
            widget.tag_add("highlight", "1.0", "end")
            self.fade_highlight(widget)

    def fade_highlight(self, widget):
        alpha = 1.0
        def reduce_alpha():
            nonlocal alpha
            if alpha > 0:
                alpha -= 0.05
                color = self.interpolate_color("#d6eaf8", "#ecf0f1", alpha)
                widget.tag_configure("highlight", background=color)
                widget.after(50, reduce_alpha)
            else:
                widget.tag_remove("highlight", "1.0", "end")
                widget.config(state='disabled')
        reduce_alpha()

    def interpolate_color(self, start, end, alpha):
        start_rgb = self.root.winfo_rgb(start)
        end_rgb = self.root.winfo_rgb(end)
        return '#{:02x}{:02x}{:02x}'.format(
            int(start_rgb[0]/256 + (end_rgb[0]/256 - start_rgb[0]/256) * alpha),
            int(start_rgb[1]/256 + (end_rgb[1]/256 - start_rgb[1]/256) * alpha),
            int(start_rgb[2]/256 + (end_rgb[2]/256 - start_rgb[2]/256) * alpha)
        )

    def get_personal_data(self):
        return {
            "age": self.age_entry.get(),
            "gender": self.gender_var.get(),
            "weight": self.weight_entry.get(),
            "height": self.height_entry.get(),
            "activity_level": self.activity_var.get(),
            "dietary_restrictions": self.restrictions_var.get(),
            "goals": self.goals_var.get(),
        }

    def get_posture_data(self):
        return {
            "issues": self.issues_entry.get(),
            "duration": self.duration_entry.get(),
            "pain_location": self.pain_entry.get(),
            "work_environment": self.work_var.get(),
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthAdvisorApp(root)
    root.mainloop()