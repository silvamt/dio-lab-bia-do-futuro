"""
Data loader module for the Proactive Financial Agent.
Validates and loads data from CSV and JSON files in the /data directory.
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from constants import (
    FILE_TRANSACTIONS, FILE_HISTORY, FILE_PROFILE, FILE_PRODUCTS,
    TRANSACTION_COLUMNS, HISTORY_COLUMNS, 
    PROFILE_REQUIRED_FIELDS, PRODUCT_REQUIRED_FIELDS
)
from security_utils import validate_file_path

logger = logging.getLogger(__name__)


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
        file_path = self.data_dir / FILE_TRANSACTIONS
        
        # Security: validate file path
        if not validate_file_path(str(file_path), str(self.data_dir)):
            raise ValueError(f"Caminho de arquivo inválido: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Erro ao ler CSV de transações: {e}")
            raise ValueError(f"Erro ao processar arquivo de transações: {str(e)}")
        
        # Validate required columns
        missing_cols = [col for col in TRANSACTION_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes em {FILE_TRANSACTIONS}: {missing_cols}")
        
        # Convert date column with error handling
        try:
            df['data'] = pd.to_datetime(df['data'])
        except Exception as e:
            logger.error(f"Erro ao converter datas: {e}")
            raise ValueError(f"Formato de data inválido em {FILE_TRANSACTIONS}")
        
        return df
    
    def _load_history(self) -> pd.DataFrame:
        """Load and validate customer service history CSV."""
        file_path = self.data_dir / FILE_HISTORY
        
        # Security: validate file path
        if not validate_file_path(str(file_path), str(self.data_dir)):
            raise ValueError(f"Caminho de arquivo inválido: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Erro ao ler CSV de histórico: {e}")
            raise ValueError(f"Erro ao processar arquivo de histórico: {str(e)}")
        
        # Validate required columns
        missing_cols = [col for col in HISTORY_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias ausentes em {FILE_HISTORY}: {missing_cols}")
        
        # Convert date column with error handling
        try:
            df['data'] = pd.to_datetime(df['data'])
        except Exception as e:
            logger.error(f"Erro ao converter datas: {e}")
            raise ValueError(f"Formato de data inválido em {FILE_HISTORY}")
        
        return df
    
    def _load_investor_profile(self) -> Dict:
        """Load and validate investor profile JSON."""
        file_path = self.data_dir / FILE_PROFILE
        
        # Security: validate file path
        if not validate_file_path(str(file_path), str(self.data_dir)):
            raise ValueError(f"Caminho de arquivo inválido: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de perfil: {e}")
            raise ValueError(f"Formato JSON inválido em {FILE_PROFILE}")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de perfil: {e}")
            raise ValueError(f"Erro ao processar {FILE_PROFILE}: {str(e)}")
        
        # Validate required fields
        missing_fields = [field for field in PROFILE_REQUIRED_FIELDS if field not in profile]
        if missing_fields:
            raise ValueError(f"Campos obrigatórios ausentes em {FILE_PROFILE}: {missing_fields}")
        
        return profile
    
    def _load_products(self) -> List[Dict]:
        """Load and validate financial products JSON."""
        file_path = self.data_dir / FILE_PRODUCTS
        
        # Security: validate file path
        if not validate_file_path(str(file_path), str(self.data_dir)):
            raise ValueError(f"Caminho de arquivo inválido: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de produtos: {e}")
            raise ValueError(f"Formato JSON inválido em {FILE_PRODUCTS}")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de produtos: {e}")
            raise ValueError(f"Erro ao processar {FILE_PRODUCTS}: {str(e)}")
        
        # Validate that products is a list
        if not isinstance(products, list):
            raise ValueError(f"{FILE_PRODUCTS} deve conter uma lista de produtos")
        
        # Validate required fields in each product
        for idx, product in enumerate(products):
            missing_fields = [field for field in PRODUCT_REQUIRED_FIELDS if field not in product]
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes no produto {idx}: {missing_fields}")
        
        return products
