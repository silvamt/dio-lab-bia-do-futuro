"""
Agent logic for the Proactive Financial Agent.
Implements dynamic data-driven responses powered by LLM.
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

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
        # Convert transactions DataFrame to list of dicts
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
        
        # Convert history DataFrame to list of dicts
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
        
        return {
            'transactions': transactions_list,
            'history': history_list,
            'profile': self.profile,
            'products': self.products
        }
    
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
        """
        sources = []
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Check for transaction-related keywords
        if any(word in response_lower or word in query_lower for word in 
               ['transação', 'transações', 'gasto', 'gastos', 'despesa', 'despesas', 'gastou']):
            sources.append('transacoes.csv')
        
        # Check for profile-related keywords
        if any(word in response_lower or word in query_lower for word in 
               ['perfil', 'renda', 'salário', 'meta', 'metas', 'objetivo', 'reserva']):
            sources.append('perfil_investidor.json')
        
        # Check for product-related keywords
        if any(word in response_lower or word in query_lower for word in 
               ['produto', 'produtos', 'investimento', 'investir', 'aplicar', 'recomend']):
            sources.append('produtos_financeiros.json')
        
        # Check for history-related keywords
        if any(word in response_lower or word in query_lower for word in 
               ['histórico', 'atendimento', 'atendimentos', 'anterior']):
            sources.append('historico_atendimento.csv')
        
        # Default to general data if no specific sources identified
        if not sources:
            sources.append('dados do sistema')
        
        return sources

