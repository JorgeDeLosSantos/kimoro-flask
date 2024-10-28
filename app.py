from flask import Flask, render_template, request, send_file
import matplotlib.pyplot as plt
import moro as mr
import sympy as sp
import json
import random

app = Flask(__name__)

# Global vars

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/forward-kinematics", methods=["GET", "POST"])
def forward_kinematics():
    fkdata_filename = "fk_data.json"
    try:
        saved_data = load_data(fkdata_filename)
        robot_dof = saved_data.get("robot_dof") 
        fk_str_latex = saved_data.get("fk_str_latex")
        dh_params = saved_data.get("dh_params")
        new_calc = saved_data.get("new_calc")
    except Exception as e:
        robot_dof = 6
        fk_str_latex = ""
        dh_params = []
        new_calc = True
        
    # print(robot_dof, fk_str_latex, dh_params, new_calc)
    
    if request.method == "POST":
        form_id = request.form.get("form_id")   
        
        if form_id == "dof_form":
            robot_dof = int(request.form.get("dof"))
            new_calc = True
            
        if form_id == "dh_params_form":
            # Leer los parámetros de Denavit-Hartenberg del formulario
            # robot_dof = int(request.form.get("dof"))
            dh_params = []
            for i in range(robot_dof):
                a = request.form.get(f"a_{i}", 0)
                alpha = request.form.get(f"alpha_{i}", 0)
                d = request.form.get(f"d_{i}", 0)
                theta = request.form.get(f"theta_{i}", 0)
                a,alpha,d,theta = preprocess_params(a,alpha,d,theta)
                dh_params.append((a, alpha, d, theta))

            # Calcular la cinemática directa y generar la imagen
            Robot = mr.Robot(*dh_params)
            fk_str_latex = f"T_{robot_dof}^0 = " + sp.latex( Robot.T )
            new_calc = False
            # return render_template("Robot.html", fk=fk)
    context = {
        "robot_dof": robot_dof, 
        "selected_value": robot_dof,
        "fk": fk_str_latex,
        "dh_params": [(str(a), str(alpha), str(d), str(theta)) for (a,alpha,d,theta) in dh_params],
        "new_calc": new_calc,
        }
    
    save_data(context, fkdata_filename)
    return render_template("forward-kinematics.html", **context)

@app.route("/inverse-kinematics", methods=["GET", "POST"])
def inverse_kinematics():
    ikdata_filename = "ik_data.json"
    try:
        saved_data = load_data(ikdata_filename)
        robot_dof = saved_data.get("robot_dof") 
        fk_str_latex = saved_data.get("fk_str_latex")
        dh_params = saved_data.get("dh_params")
        new_calc = saved_data.get("new_calc")
    except Exception as e:
        robot_dof = 6
        fk_str_latex = ""
        dh_params = [("","","","")]
        new_calc = True
        
    if request.method == "POST":
        form_id = request.form.get("form_id")   
        # print(f"theta_0 = {request.form.get('theta_0')}")
        # print(f"a_0 = {request.form.get('a_0')}")
        
        if form_id == "dof_form":
            robot_dof = int(request.form.get("dof"))
            new_calc = True
            
        if form_id == "compute_ik":
            # Leer los parámetros de Denavit-Hartenberg del formulario
            # robot_dof = int(request.form.get("dof"))
            dh_params = []
            for i in range(robot_dof):
                a = request.form.get(f"a_{i}", 0)
                alpha = request.form.get(f"alpha_{i}", 0)
                d = request.form.get(f"d_{i}", 0)
                theta = request.form.get(f"theta_{i}", 0)
                a,alpha,d,theta = preprocess_params(a,alpha,d,theta)
                dh_params.append((a, alpha, d, theta))
                
            Px = sp.sympify( request.form.get("Px") )
            Py = sp.sympify( request.form.get("Py") )
            Pz = sp.sympify( request.form.get("Pz") )
            r_des = sp.Matrix( [Px,Py] )
            # Calcular la cinemática directa y generar la imagen
            Robot = mr.Robot(*dh_params)
            r_e = Robot.T[:2,3]
            print(Robot.qs)
            q_sol = sp.nsolve(sp.Eq(r_e, r_des), Robot.qs, [0.1,0.1])
            print( q_sol )
            # fk_str_latex = f"T_{robot_dof}^0 = " + sp.latex( Robot.T )
            fk_str_latex = f"{q_sol}"
            new_calc = False
    
    # print(robot_dof, fk_str_latex, dh_params)   
    context = {
        "robot_dof": robot_dof, 
        "selected_value": robot_dof,
        "fk": fk_str_latex,
        "new_calc": new_calc,
        "dh_params": [(str(a), str(alpha), str(d), str(theta)) for (a,alpha,d,theta) in dh_params],
        }
    
    save_data(context, ikdata_filename)
    return render_template("inverse-kinematics.html", **context)


def preprocess_params(a,alpha,d,theta):
    context = get_moro_vars()
    a = sp.sympify(a, locals=context)
    alpha = sp.sympify(alpha, locals=context)
    d = sp.sympify(d, locals=context)
    theta = sp.sympify(theta, locals=context)
    return a,alpha,d,theta

def get_moro_vars():
    context_vars = {
        "l1": mr.l1,
        "l2": mr.l2,
        "l3": mr.l3,
        "l4": mr.l4,
        "l5": mr.l5,
        "l6": mr.l6,
        "q1": mr.q1,
        "q2": mr.q2,
        "q3": mr.q3,
        "q4": mr.q4,
        "q5": mr.q5,
        "q6": mr.q6
    }
    return context_vars


def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file)

def load_data(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError


if __name__ == "__main__":
    app.run(debug=True)
