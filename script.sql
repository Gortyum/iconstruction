-- =============================================
-- SCRIPT MYSQL PARA SISTEMA DE GESTIÓN DE OBRAS
-- =============================================

SET FOREIGN_KEY_CHECKS = 0;

-- ======== TABLAS BÁSICAS Y CATALOGOS ========

CREATE TABLE Comuna (
    codigo_comuna INT AUTO_INCREMENT PRIMARY KEY,
    nombre_comuna VARCHAR(150) NOT NULL
);

CREATE TABLE CategoriaObra (
    codigo_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(150) NOT NULL
);

CREATE TABLE EstadoObra (
    codigo_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado VARCHAR(100) NOT NULL
);

CREATE TABLE Especializacion (
    codigo_especializacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_especializacion VARCHAR(150) NOT NULL
);

CREATE TABLE TipoMaterial (
    codigo_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(150) NOT NULL
);

CREATE TABLE MarcaMaterial (
    codigo_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre_marca VARCHAR(150) NOT NULL
);

CREATE TABLE TipoBodega (
    codigo_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(150) NOT NULL
);

CREATE TABLE CategoriaHerramienta (
    codigo_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(150) NOT NULL
);

CREATE TABLE TipoHerramienta (
    codigo_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo VARCHAR(150) NOT NULL
);

CREATE TABLE MarcaHerramienta (
    codigo_marca INT AUTO_INCREMENT PRIMARY KEY,
    nombre_marca VARCHAR(150) NOT NULL
);

CREATE TABLE EstadoHerramienta (
    codigo_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado VARCHAR(100) NOT NULL
);

CREATE TABLE Cargo (
    codigo_cargo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cargo VARCHAR(150) NOT NULL
);

-- ======== TABLA OBRAS ========

CREATE TABLE Obra (
    codigo_obra INT AUTO_INCREMENT PRIMARY KEY,
    nombre_obra VARCHAR(200) NOT NULL,
    direccion_obra VARCHAR(300),
    metros_cuadrados DECIMAL(12,2),
    fecha_inicio DATE,
    fecha_termino DATE,
    codigo_estado INT NOT NULL,
    codigo_categoria INT NOT NULL,
    codigo_comuna INT NOT NULL,
    FOREIGN KEY (codigo_estado) REFERENCES EstadoObra(codigo_estado),
    FOREIGN KEY (codigo_categoria) REFERENCES CategoriaObra(codigo_categoria),
    FOREIGN KEY (codigo_comuna) REFERENCES Comuna(codigo_comuna)
);

-- ======== TABLA USUARIOS ========

CREATE TABLE Usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'BODEGUERO',
    telefono VARCHAR(15),
    rut VARCHAR(12) UNIQUE,
    fecha_contratacion DATE,
    activo BOOLEAN DEFAULT TRUE,
    supervisor_id INT,
    CHECK (rol IN ('ADMIN', 'BODEGUERO', 'SUPERVISOR'))
);

-- ======== TABLA SUPERVISORES ========

CREATE TABLE Supervisor (
    id_supervisor INT AUTO_INCREMENT PRIMARY KEY,
    nombre_supervisor VARCHAR(150) NOT NULL,
    apellido_supervisor VARCHAR(150) NOT NULL,
    codigo_obra INT NOT NULL,
    codigo_especializacion INT,
    FOREIGN KEY (codigo_obra) REFERENCES Obra(codigo_obra),
    FOREIGN KEY (codigo_especializacion) REFERENCES Especializacion(codigo_especializacion)
);

-- Actualizar la tabla Usuario para agregar la FK a Supervisor
ALTER TABLE Usuario ADD CONSTRAINT fk_usuario_supervisor 
    FOREIGN KEY (supervisor_id) REFERENCES Supervisor(id_supervisor) ON DELETE SET NULL;

-- ======== TABLA INFORMES ========

CREATE TABLE Informe (
    codigo_informe INT AUTO_INCREMENT PRIMARY KEY,
    titulo_informe VARCHAR(250) NOT NULL,
    fecha_informe DATETIME DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT,
    id_supervisor INT NOT NULL,
    FOREIGN KEY (id_supervisor) REFERENCES Supervisor(id_supervisor)
);

-- ======== TABLA MATERIALES ========

CREATE TABLE Material (
    codigo_material INT AUTO_INCREMENT PRIMARY KEY,
    nombre_material VARCHAR(200) NOT NULL,
    precio_material DECIMAL(12,2) DEFAULT 0,
    codigo_tipo INT,
    codigo_marca INT,
    FOREIGN KEY (codigo_tipo) REFERENCES TipoMaterial(codigo_tipo) ON DELETE SET NULL,
    FOREIGN KEY (codigo_marca) REFERENCES MarcaMaterial(codigo_marca) ON DELETE SET NULL
);

CREATE TABLE ObraMaterial (
    codigo_obra INT NOT NULL,
    codigo_material INT NOT NULL,
    cantidad_asignada DECIMAL(12,2) NOT NULL,
    fecha_asignacion DATE,
    PRIMARY KEY (codigo_obra, codigo_material),
    FOREIGN KEY (codigo_obra) REFERENCES Obra(codigo_obra) ON DELETE CASCADE,
    FOREIGN KEY (codigo_material) REFERENCES Material(codigo_material) ON DELETE CASCADE
);

-- ======== TABLA BODEGAS ========

CREATE TABLE Bodega (
    codigo_bodega INT AUTO_INCREMENT PRIMARY KEY,
    nombre_bodega VARCHAR(200) NOT NULL,
    direccion_bodega VARCHAR(300),
    capacidad DECIMAL(12,2),
    codigo_tipo INT,
    FOREIGN KEY (codigo_tipo) REFERENCES TipoBodega(codigo_tipo) ON DELETE SET NULL
);

CREATE TABLE Bodeguero (
    id_bodeguero INT AUTO_INCREMENT PRIMARY KEY,
    nombre_bodeguero VARCHAR(150) NOT NULL,
    apellido_bodeguero VARCHAR(150) NOT NULL,
    sueldo DECIMAL(12,2)
);

CREATE TABLE BodegueroBodega (
    codigo_bodega INT NOT NULL,
    id_bodeguero INT NOT NULL,
    PRIMARY KEY (codigo_bodega, id_bodeguero),
    FOREIGN KEY (codigo_bodega) REFERENCES Bodega(codigo_bodega) ON DELETE CASCADE,
    FOREIGN KEY (id_bodeguero) REFERENCES Bodeguero(id_bodeguero) ON DELETE CASCADE
);

CREATE TABLE MaterialBodega (
    codigo_material INT NOT NULL,
    codigo_bodega INT NOT NULL,
    cantidad_almacenada DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (codigo_material, codigo_bodega),
    FOREIGN KEY (codigo_material) REFERENCES Material(codigo_material) ON DELETE CASCADE,
    FOREIGN KEY (codigo_bodega) REFERENCES Bodega(codigo_bodega) ON DELETE CASCADE
);

-- ======== TABLA HERRAMIENTAS ========

CREATE TABLE Herramienta (
    codigo_herramienta INT AUTO_INCREMENT PRIMARY KEY,
    nombre_herramienta VARCHAR(200) NOT NULL,
    precio_herramienta DECIMAL(12,2) DEFAULT 0,
    dimensiones VARCHAR(200),
    codigo_tipo INT,
    codigo_categoria INT,
    codigo_marca INT,
    codigo_estado INT,
    FOREIGN KEY (codigo_tipo) REFERENCES TipoHerramienta(codigo_tipo) ON DELETE SET NULL,
    FOREIGN KEY (codigo_categoria) REFERENCES CategoriaHerramienta(codigo_categoria) ON DELETE SET NULL,
    FOREIGN KEY (codigo_marca) REFERENCES MarcaHerramienta(codigo_marca) ON DELETE SET NULL,
    FOREIGN KEY (codigo_estado) REFERENCES EstadoHerramienta(codigo_estado) ON DELETE SET NULL
);

CREATE TABLE HerramientaBodega (
    codigo_herramienta INT NOT NULL,
    codigo_bodega INT NOT NULL,
    cantidad_almacenada INT DEFAULT 0,
    PRIMARY KEY (codigo_herramienta, codigo_bodega),
    FOREIGN KEY (codigo_herramienta) REFERENCES Herramienta(codigo_herramienta) ON DELETE CASCADE,
    FOREIGN KEY (codigo_bodega) REFERENCES Bodega(codigo_bodega) ON DELETE CASCADE
);

-- ======== TABLA OBREROS ========

CREATE TABLE Obrero (
    id_obrero INT AUTO_INCREMENT PRIMARY KEY,
    nombre_obrero VARCHAR(150) NOT NULL,
    apellido_obrero VARCHAR(150) NOT NULL,
    codigo_obra INT,
    codigo_cargo INT,
    FOREIGN KEY (codigo_obra) REFERENCES Obra(codigo_obra) ON DELETE SET NULL,
    FOREIGN KEY (codigo_cargo) REFERENCES Cargo(codigo_cargo) ON DELETE SET NULL
);

CREATE TABLE ObreroHerramienta (
    id_obrero INT NOT NULL,
    codigo_herramienta INT NOT NULL,
    fecha_inicio_uso DATE,
    fecha_termino_uso DATE,
    PRIMARY KEY (id_obrero, codigo_herramienta),
    FOREIGN KEY (id_obrero) REFERENCES Obrero(id_obrero) ON DELETE CASCADE,
    FOREIGN KEY (codigo_herramienta) REFERENCES Herramienta(codigo_herramienta) ON DELETE CASCADE
);

-- ======== TABLA PRÉSTAMOS ========

CREATE TABLE PrestamoMaterial (
    codigo_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_obrero INT NOT NULL,
    codigo_material INT NOT NULL,
    cantidad_prestada DECIMAL(12,2) NOT NULL,
    fecha_prestamo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion_esperada DATE,
    observaciones TEXT,
    devuelto BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_obrero) REFERENCES Obrero(id_obrero),
    FOREIGN KEY (codigo_material) REFERENCES Material(codigo_material)
);

CREATE TABLE DevolucionMaterial (
    codigo_devolucion INT AUTO_INCREMENT PRIMARY KEY,
    codigo_prestamo INT NOT NULL,
    cantidad_devuelta DECIMAL(12,2) NOT NULL,
    cantidad_usada DECIMAL(12,2) DEFAULT 0,
    merma DECIMAL(12,2) DEFAULT 0,
    fecha_devolucion DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (codigo_prestamo) REFERENCES PrestamoMaterial(codigo_prestamo)
);

CREATE TABLE PrestamoHerramienta (
    codigo_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_obrero INT NOT NULL,
    codigo_herramienta INT NOT NULL,
    fecha_prestamo DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion_esperada DATE,
    fecha_devolucion_real DATETIME,
    estado_al_prestar VARCHAR(100),
    estado_al_devolver VARCHAR(100),
    observaciones_prestamo TEXT,
    observaciones_devolucion TEXT,
    devuelto BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_obrero) REFERENCES Obrero(id_obrero),
    FOREIGN KEY (codigo_herramienta) REFERENCES Herramienta(codigo_herramienta)
);

-- ======== TABLAS DE AUDITORÍA ========

CREATE TABLE SesionUsuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME,
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id) ON DELETE CASCADE
);

CREATE TABLE LogActividad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    accion VARCHAR(20) NOT NULL,
    modelo VARCHAR(100),
    objeto_id INT,
    descripcion TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    CHECK (accion IN ('CREATE', 'UPDATE', 'DELETE', 'VIEW', 'LOGIN', 'LOGOUT', 'PRESTAMO', 'DEVOLUCION')),
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id) ON DELETE SET NULL
);

-- ======== ÍNDICES ADICIONALES ========

CREATE INDEX idx_obra_estado ON Obra(codigo_estado);
CREATE INDEX idx_obra_categoria ON Obra(codigo_categoria);
CREATE INDEX idx_obra_comuna ON Obra(codigo_comuna);
CREATE INDEX idx_material_tipo ON Material(codigo_tipo);
CREATE INDEX idx_material_marca ON Material(codigo_marca);
CREATE INDEX idx_herramienta_tipo ON Herramienta(codigo_tipo);
CREATE INDEX idx_herramienta_estado ON Herramienta(codigo_estado);
CREATE INDEX idx_prestamo_material_fecha ON PrestamoMaterial(fecha_prestamo);
CREATE INDEX idx_prestamo_herramienta_fecha ON PrestamoHerramienta(fecha_prestamo);
CREATE INDEX idx_log_actividad_fecha ON LogActividad(fecha);
CREATE INDEX idx_log_actividad_usuario ON LogActividad(usuario_id);
CREATE INDEX idx_sesion_usuario_fecha ON SesionUsuario(fecha_inicio);

SET FOREIGN_KEY_CHECKS = 1;

-- ======== COMENTARIOS SOBRE LAS TABLAS ========

ALTER TABLE Usuario COMMENT = 'Tabla de usuarios del sistema con roles personalizados';
ALTER TABLE Obra COMMENT = 'Tabla de obras de construcción';
ALTER TABLE Material COMMENT = 'Tabla de materiales de construcción';
ALTER TABLE Herramienta COMMENT = 'Tabla de herramientas de construcción';
ALTER TABLE PrestamoMaterial COMMENT = 'Tabla de préstamos de materiales a obreros';
ALTER TABLE LogActividad COMMENT = 'Tabla de log de actividades del sistema para auditoría';