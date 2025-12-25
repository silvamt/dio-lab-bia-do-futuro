"""
Agent logic for the Proactive Financial Agent.
Implements deterministic rules for alerts and financial planning.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class FinancialAgent:
    """Implements proactive financial agent logic."""
    
    def __init__(self, transactions_df: pd.DataFrame, history_df: pd.DataFrame,
                 investor_profile: Dict, products: List[Dict]):
        """Initialize agent with loaded data."""
        self.transactions = transactions_df
        self.history = history_df
        self.profile = investor_profile
        self.products = products
    
    def detect_spending_increase(self, days: int = 7) -> Tuple[bool, str, List[str]]:
        """
        Detect atypical spending increase comparing last N days with previous period.
        
        Returns:
            Tuple of (alert_detected, message, sources)
        """
        if len(self.transactions) < 2:
            return False, "Dados insuficientes para análise de gastos. Adicione mais transações.", ["transacoes.csv"]
        
        try:
            # Get expenses only
            expenses = self.transactions[self.transactions['tipo'] == 'saida'].copy()
            
            if len(expenses) == 0:
                return False, "Sem despesas registradas para análise.", ["transacoes.csv:tipo"]
            
            # Get date range
            latest_date = expenses['data'].max()
            period_start = latest_date - timedelta(days=days)
            previous_start = period_start - timedelta(days=days)
            
            # Calculate spending for each period
            recent_expenses = expenses[expenses['data'] >= period_start]
            previous_expenses = expenses[(expenses['data'] >= previous_start) & 
                                        (expenses['data'] < period_start)]
            
            if len(previous_expenses) == 0:
                return False, "Período anterior sem dados para comparação.", ["transacoes.csv:data,valor"]
            
            recent_total = recent_expenses['valor'].sum()
            previous_total = previous_expenses['valor'].sum()
            
            # Detect significant increase (>20%)
            if recent_total > previous_total * 1.2:
                increase_pct = ((recent_total - previous_total) / previous_total) * 100
                msg = (f"Seus gastos aumentaram {increase_pct:.0f}% nos últimos {days} dias. "
                       f"Pode ser um bom momento para revisar o orçamento.")
                return True, msg, ["transacoes.csv:data,valor,tipo"]
            
            return False, "", []
            
        except Exception as e:
            return False, f"Erro ao analisar gastos: {str(e)}", ["transacoes.csv"]
    
    def detect_recurring_expenses(self) -> Tuple[bool, str, List[str]]:
        """
        Detect recurring expenses by category or description.
        
        Returns:
            Tuple of (found, message, sources)
        """
        if len(self.transactions) < 2:
            return False, "Dados insuficientes para detectar recorrências.", ["transacoes.csv"]
        
        try:
            expenses = self.transactions[self.transactions['tipo'] == 'saida'].copy()
            
            if len(expenses) == 0:
                return False, "Sem despesas registradas.", ["transacoes.csv:tipo"]
            
            # Group by category and count occurrences
            category_counts = expenses['categoria'].value_counts()
            
            # Find categories with 2+ occurrences
            recurring = category_counts[category_counts >= 2]
            
            if len(recurring) > 0:
                top_category = recurring.index[0]
                count = recurring.iloc[0]
                total = expenses[expenses['categoria'] == top_category]['valor'].sum()
                
                msg = (f"Você tem {count} despesas em '{top_category}' totalizando R$ {total:.2f}. "
                       f"Considere analisar se há oportunidade de redução.")
                return True, msg, ["transacoes.csv:categoria,valor"]
            
            return False, "", []
            
        except Exception as e:
            return False, f"Erro ao detectar recorrências: {str(e)}", ["transacoes.csv"]
    
    def calculate_goal_planning(self, goal_value: float, months: int) -> Tuple[bool, str, List[str]]:
        """
        Calculate monthly amount needed to reach a financial goal.
        
        Args:
            goal_value: Target amount
            months: Time horizon in months
            
        Returns:
            Tuple of (success, message, sources)
        """
        if months <= 0:
            return False, "Prazo inválido para meta financeira. Informe um prazo em meses maior que zero.", []
        
        try:
            monthly_needed = goal_value / months
            income = self.profile.get('renda_mensal', 0)
            
            if income == 0:
                return False, "Renda mensal não informada no perfil.", ["perfil_investidor.json:renda_mensal"]
            
            pct_income = (monthly_needed / income) * 100
            
            profile_type = self.profile.get('perfil_investidor', 'moderado')
            
            msg = (f"Para atingir R$ {goal_value:.2f} em {months} meses, reserve R$ {monthly_needed:.2f} mensais. "
                   f"Isso representa {pct_income:.1f}% da sua renda ({profile_type}).")
            
            return True, msg, ["perfil_investidor.json:renda_mensal,perfil_investidor"]
            
        except Exception as e:
            return False, f"Erro ao calcular planejamento: {str(e)}", ["perfil_investidor.json"]
    
    def suggest_product(self) -> Tuple[bool, str, List[str]]:
        """
        Suggest financial product based on investor profile.
        
        Returns:
            Tuple of (success, message, sources)
        """
        if not self.products:
            return False, "Produtos financeiros não disponíveis.", ["produtos_financeiros.json"]
        
        try:
            profile_type = self.profile.get('perfil_investidor', 'moderado').lower()
            accepts_risk = self.profile.get('aceita_risco', False)
            
            # Map profile to risk level
            risk_mapping = {
                'conservador': 'baixo',
                'moderado': 'medio' if accepts_risk else 'baixo',
                'arrojado': 'alto'
            }
            
            target_risk = risk_mapping.get(profile_type, 'baixo')
            
            # Filter products by risk
            suitable_products = [p for p in self.products if p['risco'] == target_risk]
            
            if not suitable_products:
                # Fallback to low risk
                suitable_products = [p for p in self.products if p['risco'] == 'baixo']
            
            if suitable_products:
                product = suitable_products[0]
                msg = (f"Com perfil {profile_type}, considere '{product['nome']}'. "
                       f"{product['indicado_para']}.")
                return True, msg, ["perfil_investidor.json:perfil_investidor,aceita_risco", 
                                  "produtos_financeiros.json:nome,risco,indicado_para"]
            
            return False, "Nenhum produto compatível encontrado.", ["produtos_financeiros.json"]
            
        except Exception as e:
            return False, f"Erro ao sugerir produto: {str(e)}", ["produtos_financeiros.json", "perfil_investidor.json"]
    
    def get_spending_summary(self, days: int = 30) -> Tuple[bool, str, List[str]]:
        """
        Get spending summary for last N days.
        
        Returns:
            Tuple of (success, message, sources)
        """
        if len(self.transactions) == 0:
            return False, "Sem transações registradas.", ["transacoes.csv"]
        
        try:
            expenses = self.transactions[self.transactions['tipo'] == 'saida'].copy()
            
            if len(expenses) == 0:
                return False, "Sem despesas registradas.", ["transacoes.csv:tipo"]
            
            # Filter by date
            latest_date = expenses['data'].max()
            cutoff_date = latest_date - timedelta(days=days)
            recent = expenses[expenses['data'] >= cutoff_date]
            
            if len(recent) == 0:
                return False, f"Sem despesas nos últimos {days} dias.", ["transacoes.csv:data"]
            
            total = recent['valor'].sum()
            top_category = recent.groupby('categoria')['valor'].sum().idxmax()
            top_value = recent.groupby('categoria')['valor'].sum().max()
            
            msg = (f"Você gastou R$ {total:.2f} nos últimos {days} dias. "
                   f"Maior categoria: {top_category} (R$ {top_value:.2f}).")
            
            return True, msg, ["transacoes.csv:data,tipo,categoria,valor"]
            
        except Exception as e:
            return False, f"Erro ao calcular resumo: {str(e)}", ["transacoes.csv"]
    
    def answer_query(self, query: str) -> Tuple[str, str, List[str]]:
        """
        Process user query and return appropriate response.
        
        Args:
            query: User question or command
            
        Returns:
            Tuple of (short_response, detailed_response, sources)
        """
        query_lower = query.lower().strip()
        
        # Goal planning queries
        if any(word in query_lower for word in ['meta', 'objetivo', 'poupar', 'guardar']):
            # Check if user provided goal details
            if 'metas' in self.profile and len(self.profile['metas']) > 0:
                first_goal = self.profile['metas'][0]
                goal_value = first_goal.get('valor_necessario', 0)
                
                # Calculate months from deadline
                try:
                    deadline = datetime.strptime(first_goal.get('prazo', ''), '%Y-%m')
                    months = max(1, (deadline.year - datetime.now().year) * 12 + 
                                deadline.month - datetime.now().month)
                except:
                    months = 12  # Default to 1 year
                
                success, msg, sources = self.calculate_goal_planning(goal_value, months)
                return msg, msg, sources
            else:
                return ("Informe seu objetivo e prazo para calcular valor mensal. "
                       "Qual meta deseja alcançar?"), "", ["perfil_investidor.json:metas"]
        
        # Spending queries
        elif any(word in query_lower for word in ['gasto', 'gastei', 'despesa', 'quanto']):
            success, msg, sources = self.get_spending_summary()
            return msg, msg, sources
        
        # Alert queries
        elif any(word in query_lower for word in ['alerta', 'aumento', 'aumentou']):
            success, msg, sources = self.detect_spending_increase()
            if success:
                return msg, msg, sources
            else:
                # Try recurring expenses
                success, msg, sources = self.detect_recurring_expenses()
                if success:
                    return msg, msg, sources
                else:
                    return "Sem alertas no momento. Seus gastos estão estáveis.", "", ["transacoes.csv"]
        
        # Investment/product queries
        elif any(word in query_lower for word in ['investir', 'produto', 'aplicar', 'recomendar']):
            success, msg, sources = self.suggest_product()
            return msg, msg, sources
        
        # Greetings
        elif any(word in query_lower for word in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite']):
            name = self.profile.get('nome', 'Cliente')
            return (f"Olá, {name}. Estou aqui para ajudar com suas finanças. "
                   "Como posso ajudar hoje?"), "", []
        
        # Default response
        else:
            return ("Posso ajudar com: gastos, alertas, metas ou produtos financeiros. "
                   "Sobre qual tema deseja falar?"), "", []
