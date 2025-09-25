import os
import time
import logging
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from flask import Flask
import threading

# Configurar Flask
app = Flask(_name_)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RenderTradingEngine:
    def _init_(self):
        # Variables de entorno de Render
        self.api_key = os.environ.get('BINANCE_API_KEY')
        self.api_secret = os.environ.get('BINANCE_API_SECRET')
        self.testnet = os.environ.get('TESTNET', 'True').lower() == 'true'
        
        if not self.api_key or not self.api_secret:
            logging.error("❌ API Keys no configuradas")
            return
            
        self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)
        self.symbol = 'BTCUSDT'
        self.is_running = True
        self.cycle_count = 0
        
        logging.info(f"✅ Motor configurado - Modo: {'TESTNET' if self.testnet else 'PRODUCCIÓN'}")
    
    def get_system_status(self):
        """Obtener estado del sistema"""
        try:
            price_data = self.client.get_symbol_ticker(symbol=self.symbol)
            usdt_balance = self.client.get_asset_balance(asset='USDT')
            btc_balance = self.client.get_asset_balance(asset='BTC')
            
            return {
                'status': 'active',
                'cycle': self.cycle_count,
                'price': float(price_data['price']),
                'usdt_balance': float(usdt_balance['free']) if usdt_balance else 0,
                'btc_balance': float(btc_balance['free']) if btc_balance else 0,
                'timestamp': datetime.now().isoformat(),
                'mode': 'TESTNET' if self.testnet else 'PRODUCTION'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def run_trading_cycle(self):
        """Ejecutar un ciclo de trading"""
        try:
            status = self.get_system_status()
            if status['status'] == 'active':
                logging.info(f"🔁 Ciclo {self.cycle_count} - BTC: ${status['price']:,.2f}")
            self.cycle_count += 1
        except Exception as e:
            logging.error(f"❌ Error en ciclo: {e}")
    
    def start_engine(self):
        """Iniciar motor en segundo plano"""
        def run():
            while self.is_running:
                self.run_trading_cycle()
                time.sleep(300)  # 5 minutos entre ciclos
                
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        logging.info("🚀 Motor iniciado en segundo plano")

# Crear instancia global
engine = RenderTradingEngine()

# Endpoints de Flask
@app.route('/')
def home():
    return {
        'service': 'Binance Trading Engine',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': ['/status', '/start', '/health']
    }

@app.route('/status')
def status():
    return engine.get_system_status()

@app.route('/start')
def start():
    engine.start_engine()
    return {'message': 'Motor iniciado'}

@app.route('/health')
def health():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

# Iniciar automáticamente al desplegar
engine.start_engine()

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
