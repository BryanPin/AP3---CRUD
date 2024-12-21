from flask import Flask, render_template, request, redirect, url_for, session
import MySQLdb

app = Flask(__name__)
app.secret_key = 'secret_key'  # Asegúrate de definir una clave secreta para las sesiones

# Conexión a la base de datos
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="inventario")
cursor = db.cursor()

# Ruta para la página principal (inventario)
@app.route('/')
@app.route('/')
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtener el nombre del usuario desde la sesión
    username = session['username']
    
    # Obtener el término de búsqueda desde la consulta GET
    buscar = request.args.get('buscar', '')
    
    # Si hay un término de búsqueda, buscamos en la base de datos
    if buscar:
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE %s OR descripcion LIKE %s", 
                       ('%' + buscar + '%', '%' + buscar + '%'))
    else:
        cursor.execute("SELECT * FROM productos")
    
    productos = cursor.fetchall()
    
    return render_template('index.html', productos=productos, username=username)



# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s", (nombre_usuario, contrasena))
        usuario = cursor.fetchone()
        
        if usuario:
            session['username'] = nombre_usuario  # Guardamos el nombre de usuario en la sesión
            return redirect(url_for('index'))
        else:
            return "Usuario o contraseña incorrectos", 401

    return render_template('login.html')

# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        
        # Comprobar si el nombre de usuario ya existe
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        usuario = cursor.fetchone()
        
        if usuario:
            return "Este nombre de usuario ya existe", 400
        else:
            cursor.execute("INSERT INTO usuarios (nombre_usuario, contrasena) VALUES (%s, %s)", (nombre_usuario, contrasena))
            db.commit()
            return redirect(url_for('login'))

    return render_template('register.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)  # Eliminamos el nombre de usuario de la sesión
    return redirect(url_for('login'))  # Redirigimos al login después de cerrar sesión

# Resto de las rutas como agregar, editar, eliminar productos siguen igual...


# Ruta para agregar un nuevo producto
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        
        cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio) VALUES (%s, %s, %s, %s)", 
                       (nombre, descripcion, cantidad, precio))
        db.commit()
        return redirect(url_for('index'))
    
    return render_template('agregar.html')

# Ruta para editar un producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        
        cursor.execute("""
            UPDATE productos 
            SET nombre = %s, descripcion = %s, cantidad = %s, precio = %s
            WHERE id = %s
        """, (nombre, descripcion, cantidad, precio, id))
        db.commit()
        return redirect(url_for('index'))
    
    return render_template('editar.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/eliminar/<int:id>')
def eliminar(id):
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
