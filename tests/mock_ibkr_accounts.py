"""
Mock tests for IBKR Accounts tool.
This script tests the AccountsManager logic by mocking the IBKRClient.
"""
import unittest
from unittest.mock import MagicMock, patch
from tools.ibkr.ibkr_accounts.core import AccountsManager
from tools.ibkr.schemas.account_schemas import SetDynamicAccountRequest

class TestIBKRAccounts(unittest.TestCase):
    """
    Unit tests for AccountsManager using mocked API responses.
    """
    def setUp(self):
        """
        Initialize the test case by patching dependencies.
        """
        # Patch IBKRClient and DatabaseManager to avoid real network/DB calls
        self.mock_client_patcher = patch('tools.ibkr.ibkr_accounts.core.IBKRClient')
        self.mock_db_patcher = patch('tools.ibkr.common.logger.db_manager')
        
        self.mock_client_class = self.mock_client_patcher.start()
        self.mock_db_manager = self.mock_db_patcher.start()
        
        self.mock_client = self.mock_client_class.return_value
        self.manager = AccountsManager()

    def tearDown(self):
        """
        Clean up patchers after each test.
        """
        self.mock_client_patcher.stop()
        self.mock_db_patcher.stop()

    def test_list_accounts(self):
        """
        Test retrieving the list of brokerage accounts.
        """
        # Mock Response for /iserver/accounts
        self.mock_client.get.return_value = {
            "accounts": ["U1234567"],
            "aliases": {"U1234567": "MyAccount"},
            "selectedAccount": "U1234567"
        }
        
        res = self.manager.list_accounts()
        self.assertEqual(len(res.accounts), 1)
        self.assertEqual(res.selectedAccount, "U1234567")
        self.mock_client.get.assert_called_with("/iserver/accounts")

    def test_get_pnl(self):
        """
        Test retrieving PnL data for the session.
        """
        # Mock Response for /iserver/account/pnl/partitioned
        self.mock_client.get.return_value = {
            "upnl": {
                "U1234567": {
                    "rowType": 1,
                    "pnl": 1000.5,
                    "dpl": 10.0,
                    "upl": 900.0,
                    "rpl": 100.5
                }
            }
        }
        
        res = self.manager.get_pnl()
        self.assertIn("U1234567", res.upnl)
        self.assertEqual(res.upnl["U1234567"].pnl, 1000.5)
        self.mock_client.get.assert_called_with("/iserver/account/pnl/partitioned")

    def test_get_signatures_and_owners(self):
        """
        Test retrieving signature and ownership information.
        """
        # Mock Response for /acesws/{accountId}/signatures-and-owners
        self.mock_client.get.return_value = {
            "accountId": "DU7126953",
            "users": [
                {
                    "roleId": "OWNER",
                    "hasRightCodeInd": True,
                    "userName": "rhibkv557",
                    "entity": {
                        "firstName": "Juan",
                        "lastName": "Noguera Rodriguez",
                        "entityType": "INDIVIDUAL",
                        "entityName": "Mr. Juan  Noguera Rodriguez",
                        "dateOfBirth": "1968-09-13"
                    }
                }
            ],
            "applicant": {
                "signatures": [
                    "Juan Noguera Rodriguez"
                ]
            }
        }
        
        res = self.manager.get_signatures_and_owners("DU7126953")
        self.assertEqual(res.accountId, "DU7126953")
        self.assertEqual(len(res.users), 1)
        self.assertEqual(res.users[0].entity.entityType, "INDIVIDUAL")
        self.assertEqual(len(res.applicant.signatures), 1)
        self.assertEqual(res.applicant.signatures[0], "Juan Noguera Rodriguez")
        self.mock_client.get.assert_called_with("/acesws/DU7126953/signatures-and-owners")

    def test_search_dynamic_accounts(self):
        """
        Test searching for dynamic accounts.
        """
        self.mock_client.get.return_value = [
            {"accountId": "DU12345", "accountName": "Dynamic Acc 1"},
            {"accountId": "DU67890", "accountName": "Dynamic Acc 2"}
        ]
        res = self.manager.search_dynamic_accounts("Dynamic")
        self.assertEqual(len(res.accounts), 2)
        self.assertEqual(res.accounts[0].accountId, "DU12345")
        self.mock_client.get.assert_called_with("/iserver/account/search/Dynamic")

    def test_get_account_summary(self):
        """
        Test retrieving account summary.
        """
        self.mock_client.get.return_value = {
            "accountId": "DU7126953",
            "accountType": "",
            "status": "",
            "balance": 1095732.0,
            "SMA": 0.0,
            "buyingPower": 7304882.0,
            "availableFunds": 1095732.0,
            "excessLiquidity": 1097517.0,
            "netLiquidationValue": 1115363.0,
            "equityWithLoanValue": 1115363.0,
            "regTLoan": 0.0,
            "securitiesGVP": 59487.0,
            "totalCashValue": 1055167.0,
            "accruedInterest": 0.0,
            "regTMargin": 0.0,
            "initialMargin": 19631.0,
            "maintenanceMargin": 17846.0,
            "cashBalances": [
                {"currency": "EUR", "balance": 859826.0, "settledCash": 859826.0}
            ]
        }
        res = self.manager.get_account_summary("DU7126953")
        self.assertEqual(res.accountId, "DU7126953")
        self.assertEqual(res.netLiquidationValue, 1115363.0)
        self.assertEqual(res.cashBalances[0].currency, "EUR")
        self.mock_client.get.assert_called_with("/iserver/account/DU7126953/summary")

    def test_get_available_funds(self):
        """
        Test retrieving available funds summary.
        """
        self.mock_client.get.return_value = {
            "total": {
                "current_available": "1,095,696 EUR",
                "current_excess": "1,097,479 EUR",
                "Prdctd Pst-xpry Excss": "0 EUR",
                "Lk Ahd Avlbl Fnds": "1,095,696 EUR",
                "Lk Ahd Excss Lqdty": "1,097,479 EUR",
                "overnight_available": "1,095,696 EUR",
                "overnight_excess": "1,097,479 EUR",
                "buying_power": "7,304,639 EUR",
                "leverage": "n/a",
                "Lk Ahd Nxt Chng": "@ 22:00:00"
            },
            "cfd": {
                "leverage": "0.05"
            }
        }
        res = self.manager.get_available_funds("DU7126953")
        self.assertEqual(res.total.current_available, "1,095,696 EUR")
        self.assertEqual(res.cfd.leverage, "0.05")
        self.mock_client.get.assert_called_with("/iserver/account/DU7126953/summary/available_funds")

    def test_get_account_balances(self):
        """
        Test retrieving account balances summary.
        """
        self.mock_client.get.return_value = {
            "total": {
                "net_liquidation": "1,115,312 EUR",
                "Nt Lqdtn Uncrtnty": "0 EUR",
                "equity_with_loan": "1,115,312 EUR",
                "sec_gross_pos_val": "59,441 EUR",
                "cash": "1,055,161 EUR",
                "MTD Interest": "709 EUR"
            },
            "cfd": {}
        }
        res = self.manager.get_account_balances("DU7126953")
        self.assertEqual(res.total.net_liquidation, "1,115,312 EUR")
        self.assertEqual(res.total.cash, "1,055,161 EUR")
        self.mock_client.get.assert_called_with("/iserver/account/DU7126953/summary/balances")

    def test_get_margin_summary(self):
        """
        Test retrieving account margin summary.
        """
        self.mock_client.get.return_value = {
            "total": {
                "current_initial": "19,616 EUR",
                "Prdctd Pst-xpry Mrgn @ Opn": "0 EUR",
                "current_maint": "17,832 EUR",
                "projected_liquidity_inital_margin": "19,616 EUR",
                "Prjctd Lk Ahd Mntnnc Mrgn": "17,832 EUR",
                "projected_overnight_initial_margin": "19,616 EUR",
                "Prjctd Ovrnght Mntnnc Mrgn": "17,832 EUR"
            },
            "cfd": {}
        }
        res = self.manager.get_margin_summary("DU7126953")
        self.assertEqual(res.total.current_initial, "19,616 EUR")
        self.assertEqual(res.total.current_maint, "17,832 EUR")
        self.mock_client.get.assert_called_with("/iserver/account/DU7126953/summary/margins")

    def test_get_market_value_summary(self):
        """
        Test retrieving account market value summary.
        """
        self.mock_client.get.return_value = {
            "EUR": {
                "total_cash": "859,826",
                "settled_cash": "859,826",
                "MTD Interest": "481",
                "stock": "0",
                "options": "0",
                "futures": "0",
                "future_options": "0",
                "funds": "0",
                "dividends_receivable": "0",
                "mutual_funds": "0",
                "money_market": "0",
                "bonds": "0",
                "Govt Bonds": "0",
                "t_bills": "0",
                "warrants": "0",
                "issuer_option": "0",
                "commodity": "0",
                "Notional CFD": "0",
                "cfd": "0",
                "net_liquidation": "860,307",
                "unrealized_pnl": "0",
                "realized_pnl": "0",
                "Exchange Rate": "1.00"
            },
            "USD": {
                "total_cash": "229,974",
                "settled_cash": "229,974",
                "MTD Interest": "268",
                "stock": "70,049",
                "options": "0",
                "futures": "0",
                "future_options": "0",
                "funds": "0",
                "dividends_receivable": "0",
                "mutual_funds": "0",
                "money_market": "0",
                "bonds": "0",
                "Govt Bonds": "0",
                "t_bills": "0",
                "warrants": "0",
                "issuer_option": "0",
                "commodity": "0",
                "Notional CFD": "0",
                "cfd": "0",
                "net_liquidation": "300,291",
                "unrealized_pnl": "20,771",
                "realized_pnl": "0",
                "Exchange Rate": "0.8493745"
            },
            "Total (in EUR)": {
                "total_cash": "1,055,160",
                "settled_cash": "1,055,160",
                "MTD Interest": "709",
                "stock": "59,498",
                "options": "0",
                "futures": "0",
                "future_options": "0",
                "funds": "0",
                "dividends_receivable": "0",
                "mutual_funds": "0",
                "money_market": "0",
                "bonds": "0",
                "Govt Bonds": "0",
                "t_bills": "0",
                "warrants": "0",
                "issuer_option": "0",
                "commodity": "0",
                "Notional CFD": "0",
                "cfd": "0",
                "net_liquidation": "1,115,367",
                "unrealized_pnl": "17,642",
                "realized_pnl": "0",
                "Exchange Rate": "1.00"
            }
        }
        res = self.manager.get_market_value_summary("DU7126953")
        self.assertIn("EUR", res.root)
        self.assertIn("USD", res.root)
        self.assertIn("Total (in EUR)", res.root)
        self.assertEqual(res.root["EUR"].net_liquidation, "860,307")
        self.assertEqual(res.root["USD"].net_liquidation, "300,291")
        self.assertEqual(res.root["Total (in EUR)"].net_liquidation, "1,115,367")
        # Verify that Cryptocurrency field is optional and not included in the response
        self.assertIsNone(res.root["EUR"].Cryptocurrency)
        self.mock_client.get.assert_called_with("/iserver/account/DU7126953/summary/market_value")

    def test_set_dynamic_account(self):
        """
        Test setting the active dynamic account.
        """
        self.mock_client.post.return_value = {
            "dynamicAccount": "DU12345",
            "message": "Dynamic account set successfully."
        }
        res = self.manager.set_dynamic_account("DU12345")
        self.assertEqual(res.dynamicAccount, "DU12345")
        self.mock_client.post.assert_called_with(
            "/iserver/dynaccount",
            data=SetDynamicAccountRequest(accountId="DU12345").model_dump_json()
        )

if __name__ == "__main__":
    unittest.main()
