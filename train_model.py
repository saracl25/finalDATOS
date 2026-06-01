import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def main():
    print("Iniciando generación de datos sintéticos...")
    np.random.seed(42)
    n_samples = 500
    
    productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Auriculares']
    precios_promedio = {
        'Laptop': 2500.0,
        'Mouse': 50.0,
        'Teclado': 120.0,
        'Monitor': 350.0,
        'Auriculares': 80.0
    }
    
    lista_prod = np.random.choice(productos, size=n_samples)
    lista_cant = np.random.randint(1, 11, size=n_samples)
    lista_prec = []
    lista_total = []
    
    for prod, cant in zip(lista_prod, lista_cant):
        base_price = precios_promedio[prod]
        unit_price = round(base_price * np.random.uniform(0.95, 1.05), 2)
        lista_prec.append(unit_price)
        
        subtotal = unit_price * cant
        if cant >= 8:
            descuento = 0.15 # 15% descuento
        elif cant >= 5:
            descuento = 0.08 # 8% descuento
        else:
            descuento = 0.0
            
        lista_total.append(round(subtotal * (1 - descuento), 2))
        
    df_historico = pd.DataFrame({
        'id_venta': range(1, n_samples + 1),
        'producto': lista_prod,
        'cantidad': lista_cant,
        'precio': lista_prec,
        'total_venta': lista_total
    })
    
    df_historico.to_csv('ventas_historicas.csv', index=False)
    print("¡Dataset 'ventas_historicas.csv' guardado exitosamente!")
    
    print("Preparando variables y aplicando One-Hot Encoding...")
    df_encoded = pd.get_dummies(df_historico, columns=['producto'], dtype=int)
    
    X = df_encoded.drop(columns=['id_venta', 'total_venta'])
    y = df_encoded['total_venta']
    columnas_modelo = list(X.columns)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Entrenando modelo Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    y_pred = rf_model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"Evaluación del Modelo:")
    print(f"  - Coeficiente R2: {r2:.4f}")
    print(f"  - Error Cuadrático Medio (RMSE): ${rmse:.2f}")
    
    model_data = {
        'model': rf_model,
        'features': columnas_modelo,
        'productos_validos': productos,
        'precios_promedio': precios_promedio
    }
    
    joblib.dump(model_data, 'modelo_ventas.pkl')
    print("¡Modelo serializado guardado como 'modelo_ventas.pkl'!")

if __name__ == "__main__":
    main()
