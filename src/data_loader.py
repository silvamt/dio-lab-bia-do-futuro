"""
Data loader module for the Proactive Financial Agent.
Validates and loads data from CSV and JSON files in the /data directory.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple


class DataLoader:
    """Handles loading and validation of financial data."""
    
    def __init__(self, data_dir: str = None):
        """Initialize data loader with data directory path."""
        if data_dir is None:
            # Default to /data directory relative to this file
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, Dict, List[Dict]]:
        """
        Load all required data files.
        
        Returns:
            Tuple containing (transactions_df, history_df, investor_profile, products_list)
        
        Raises:
            FileNotFoundError: If required files are missing
            ValueError: If data validation fails
        """
        try:
            # Load CSV files
            transactions = self._load_transactions()
            history = self._load_history()
            
            # Load JSON files
            investor_profile = self._load_investor_profile()
            products = self._load_products()
            
            return transactions, history, investor_profile, products
            
        except Exception as e:
            raise ValueError(f"Erro ao carregar dados: {str(e)}")
    
    def _load_transactions(self) -> pd.DataFrame:
        """Load and validate transactions CSV."""
        file_path = self.data_dir / "transacoes.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['data', 'descricao', 'categoria', 'valor', 'tipo']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes em transacoes.csv: {missing_cols}")
        
        # Convert date column
        df['data'] = pd.to_datetime(df['data'])
        
        return df
    
    def _load_history(self) -> pd.DataFrame:
        """Load and validate customer service history CSV."""
        file_path = self.data_dir / "historico_atendimento.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['data', 'canal', 'tema', 'resumo', 'resolvido']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes em historico_atendimento.csv: {missing_cols}")
        
        # Convert date column
        df['data'] = pd.to_datetime(df['data'])
        
        return df
    
    def _load_investor_profile(self) -> Dict:
        """Load and validate investor profile JSON."""
        file_path = self.data_dir / "perfil_investidor.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        # Validate required fields
        required_fields = ['nome', 'perfil_investidor', 'renda_mensal', 'metas']
        missing_fields = [field for field in required_fields if field not in profile]
        if missing_fields:
            raise ValueError(f"Campos obrigatórios ausentes em perfil_investidor.json: {missing_fields}")
        
        return profile
    
    def _load_products(self) -> List[Dict]:
        """Load and validate financial products JSON."""
        file_path = self.data_dir / "produtos_financeiros.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Validate that products is a list
        if not isinstance(products, list):
            raise ValueError("produtos_financeiros.json deve conter uma lista de produtos")
        
        # Validate required fields in each product
        required_fields = ['nome', 'categoria', 'risco', 'indicado_para']
        for idx, product in enumerate(products):
            missing_fields = [field for field in required_fields if field not in product]
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes no produto {idx}: {missing_fields}")
        
        return products
