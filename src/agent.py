"""
Agent logic for the Proactive Financial Agent.
Implements dynamic data-driven responses powered by LLM.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

from constants import FILE_TRANSACTIONS, FILE_PROFILE, FILE_PRODUCTS, FILE_HISTORY

logger = logging.getLogger(__name__)


class FinancialAgent:
    """Implements dynamic financial agent with LLM-powered analysis."""
    
    def __init__(self, transactions_df: pd.DataFrame, history_df: pd.DataFrame,
                 investor_profile: Dict, products: List[Dict], llm_adapter=None):
        """
        Initialize agent with loaded data.
        
        Args:
            transactions_df: Transaction history DataFrame
            history_df: Service history DataFrame
            investor_profile: Investor profile dictionary
            products: List of financial products
            llm_adapter: LLMAdapter instance for dynamic responses
        """
        self.transactions = transactions_df
        self.history = history_df
        self.profile = investor_profile
        self.products = products
        self.llm_adapter = llm_adapter
    
    def prepare_all_data(self) -> Dict[str, Any]:
        """
        Prepare all available data in a format suitable for LLM consumption.
        
        Returns:
            Dictionary with all financial data ready for LLM context
        """
        return {
            'transactions': self._prepare_transactions(),
            'history': self._prepare_history(),
            'profile': self.profile,
            'products': self.products
        }
    
    def _prepare_transactions(self) -> List[Dict]:
        """
        Convert transactions DataFrame to list of dictionaries.
        
        Returns:
            List of transaction dictionaries
        """
        transactions_list = []
        if len(self.transactions) > 0:
            for _, row in self.transactions.iterrows():
                transactions_list.append({
                    'data': row['data'].strftime('%Y-%m-%d') if pd.notna(row['data']) else 'N/A',
                    'descricao': str(row['descricao']) if pd.notna(row['descricao']) else 'N/A',
                    'categoria': str(row['categoria']) if pd.notna(row['categoria']) else 'N/A',
                    'valor': float(row['valor']) if pd.notna(row['valor']) else 0.0,
                    'tipo': str(row['tipo']) if pd.notna(row['tipo']) else 'N/A'
                })
        return transactions_list
    
    def _prepare_history(self) -> List[Dict]:
        """
        Convert history DataFrame to list of dictionaries.
        
        Returns:
            List of history dictionaries
        """
        history_list = []
        if len(self.history) > 0:
            for _, row in self.history.iterrows():
                history_list.append({
                    'data': row['data'].strftime('%Y-%m-%d') if pd.notna(row['data']) else 'N/A',
                    'canal': str(row['canal']) if pd.notna(row['canal']) else 'N/A',
                    'tema': str(row['tema']) if pd.notna(row['tema']) else 'N/A',
                    'resumo': str(row['resumo']) if pd.notna(row['resumo']) else 'N/A',
                    'resolvido': bool(row['resolvido']) if pd.notna(row['resolvido']) else False
                })
        return history_list
    
    def answer_query(self, query: str) -> Tuple[str, List[str]]:
        """
        Process user query and return dynamic response based on all available data.
        
        This is the new simplified method that delegates interpretation and analysis
        entirely to the LLM, without predefined intents or fixed logic.
        
        Args:
            query: User question or command in natural language
            
        Returns:
            Tuple of (response, sources)
        """
        if not self.llm_adapter:
            return ("Serviço de respostas não disponível. Configure uma chave de API para usar o agente.", [])
        
        try:
            # Prepare all data for LLM context
            all_data = self.prepare_all_data()
            
            # Get dynamic response from LLM
            response = self.llm_adapter.generate_dynamic_response(query, all_data)
            
            # Determine sources based on content (simple heuristic)
            sources = self._extract_sources_from_response(response, query)
            
            return (response, sources)
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return (f"Erro ao processar sua pergunta: {str(e)}", [])
    
    def _extract_sources_from_response(self, response: str, query: str) -> List[str]:
        """
        Extract likely data sources based on response content and query.
        
        This is a simple heuristic - in production, LLM could return structured sources.
        
        Args:
            response: The generated response text
            query: The original user query
            
        Returns:
            List of source file names
        """
        sources = []
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Check for transaction-related keywords
        if self._contains_transaction_keywords(response_lower, query_lower):
            sources.append(FILE_TRANSACTIONS)
        
        # Check for profile-related keywords
        if self._contains_profile_keywords(response_lower, query_lower):
            sources.append(FILE_PROFILE)
        
        # Check for product-related keywords
        if self._contains_product_keywords(response_lower, query_lower):
            sources.append(FILE_PRODUCTS)
        
        # Check for history-related keywords
        if self._contains_history_keywords(response_lower, query_lower):
            sources.append(FILE_HISTORY)
        
        # Default to general data if no specific sources identified
        if not sources:
            sources.append('dados do sistema')
        
        return sources
    
    def _contains_transaction_keywords(self, response: str, query: str) -> bool:
        """Check if text contains transaction-related keywords."""
        keywords = ['transação', 'transações', 'gasto', 'gastos', 'despesa', 'despesas', 'gastou']
        return any(word in response or word in query for word in keywords)
    
    def _contains_profile_keywords(self, response: str, query: str) -> bool:
        """Check if text contains profile-related keywords."""
        keywords = ['perfil', 'renda', 'salário', 'meta', 'metas', 'objetivo', 'reserva']
        return any(word in response or word in query for word in keywords)
    
    def _contains_product_keywords(self, response: str, query: str) -> bool:
        """Check if text contains product-related keywords."""
        keywords = ['produto', 'produtos', 'investimento', 'investir', 'aplicar', 'recomend']
        return any(word in response or word in query for word in keywords)
    
    def _contains_history_keywords(self, response: str, query: str) -> bool:
        """Check if text contains history-related keywords."""
        keywords = ['histórico', 'atendimento', 'atendimentos', 'anterior']
        return any(word in response or word in query for word in keywords)

