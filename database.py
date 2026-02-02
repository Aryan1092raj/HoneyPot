import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "scam_logs.db"


class Database:
    """
    SQLite database for logging scam conversations and extracted data.
    Creates DB and table automatically on first run.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        """Get SQLite connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def _create_table(self):
        """Create table if not exists"""
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scam_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                persona TEXT NOT NULL,
                scammer_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                strategy TEXT,
                engagement_phase TEXT,
                extracted_upi TEXT DEFAULT '[]',
                extracted_accounts TEXT DEFAULT '[]',
                extracted_ifsc TEXT DEFAULT '[]',
                extracted_phones TEXT DEFAULT '[]',
                extracted_links TEXT DEFAULT '[]',
                risk_level TEXT DEFAULT 'LOW'
            )
        """)
        conn.commit()
        conn.close()

    # ============================================================
    # WRITE OPERATIONS
    # ============================================================

    def log_conversation(self, session_id: str, persona: str,
                         scammer_message: str, agent_response: str,
                         strategy: Dict, extracted_data: Dict,
                         risk_level: str = "LOW"):
        """Log a single conversation turn"""
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO scam_logs (
                session_id, timestamp, persona,
                scammer_message, agent_response,
                strategy, engagement_phase,
                extracted_upi, extracted_accounts,
                extracted_ifsc, extracted_phones,
                extracted_links, risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().isoformat(),
            persona,
            scammer_message,
            agent_response,
            strategy.get("strategy", ""),
            strategy.get("new_phase", ""),
            json.dumps(extracted_data.get("upi_ids", [])),
            json.dumps(extracted_data.get("account_numbers", [])),
            json.dumps(extracted_data.get("ifsc_codes", [])),
            json.dumps(extracted_data.get("phone_numbers", [])),
            json.dumps(extracted_data.get("links", [])),
            risk_level
        ))
        conn.commit()
        conn.close()

    # ============================================================
    # READ OPERATIONS
    # ============================================================

    def get_session_logs(self, session_id: str) -> List[Dict]:
        """Get all logs for a session"""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT * FROM scam_logs WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_sessions(self) -> List[Dict]:
        """Get summary of all sessions"""
        conn = self._get_connection()
        rows = conn.execute("""
            SELECT 
                session_id,
                persona,
                MIN(timestamp) as started_at,
                COUNT(*) as total_messages,
                risk_level
            FROM scam_logs 
            GROUP BY session_id 
            ORDER BY started_at DESC
        """).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all_extracted_data(self) -> Dict:
        """
        Aggregate ALL extracted data across ALL sessions.
        Used for the intelligence dashboard.
        """
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM scam_logs").fetchall()
        conn.close()

        all_data = {
            "upi_ids": [],
            "account_numbers": [],
            "ifsc_codes": [],
            "phone_numbers": [],
            "links": []
        }

        for row in rows:
            for key, col in [
                ("upi_ids", "extracted_upi"),
                ("account_numbers", "extracted_accounts"),
                ("ifsc_codes", "extracted_ifsc"),
                ("phone_numbers", "extracted_phones"),
                ("links", "extracted_links")
            ]:
                try:
                    items = json.loads(row[col])
                    all_data[key].extend(items)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Deduplicate
        for key in all_data:
            all_data[key] = list(set(all_data[key]))

        return all_data

    def get_stats(self) -> Dict:
        """Get dashboard statistics"""
        conn = self._get_connection()

        total_sessions = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM scam_logs"
        ).fetchone()[0]

        total_messages = conn.execute(
            "SELECT COUNT(*) FROM scam_logs"
        ).fetchone()[0]

        high_risk = conn.execute(
            "SELECT COUNT(*) FROM scam_logs WHERE risk_level = '🔴 HIGH'"
        ).fetchone()[0]

        conn.close()

        all_data = self.get_all_extracted_data()

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "high_risk_count": high_risk,
            "total_upi_found": len(all_data["upi_ids"]),
            "total_accounts_found": len(all_data["account_numbers"]),
            "total_phones_found": len(all_data["phone_numbers"]),
            "total_links_found": len(all_data["links"])
        }

    # ============================================================
    # REPORT GENERATION
    # ============================================================

    def generate_report(self, session_id: str) -> Dict:
        """Generate full evidence report for a session"""
        logs = self.get_session_logs(session_id)
        if not logs:
            return {"error": "No logs found"}

        # Aggregate extracted data for this session
        session_data = {
            "upi_ids": [],
            "account_numbers": [],
            "ifsc_codes": [],
            "phone_numbers": [],
            "links": []
        }

        conversation = []

        for log in logs:
            conversation.append({
                "timestamp": log["timestamp"],
                "scammer": log["scammer_message"],
                "agent": log["agent_response"],
                "strategy": log["strategy"]
            })
            for key, col in [
                ("upi_ids", "extracted_upi"),
                ("account_numbers", "extracted_accounts"),
                ("ifsc_codes", "extracted_ifsc"),
                ("phone_numbers", "extracted_phones"),
                ("links", "extracted_links")
            ]:
                try:
                    items = json.loads(log[col])
                    session_data[key].extend(items)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Deduplicate
        for key in session_data:
            session_data[key] = list(set(session_data[key]))

        return {
            "session_id": session_id,
            "persona": logs[0]["persona"],
            "started_at": logs[0]["timestamp"],
            "total_exchanges": len(logs),
            "extracted_evidence": session_data,
            "conversation": conversation,
            "risk_level": logs[-1]["risk_level"]
        }

    def clear_all(self):
        """Clear all data (for reset button)"""
        conn = self._get_connection()
        conn.execute("DELETE FROM scam_logs")
        conn.commit()
        conn.close()


# ============================================================
# QUICK TEST (run: python database.py)
# ============================================================

if __name__ == "__main__":
    db = Database()

    # Test: Insert sample data
    db.log_conversation(
        session_id="test_session_001",
        persona="Elderly Teacher",
        scammer_message="Hello sir, I'm from SBI. Send money to fraudster@paytm. Account: 1234567890. Call 9876543210",
        agent_response="Oh beta, let me check... my son usually helps me with this...",
        strategy={"strategy": "STALL", "new_phase": "trust_building"},
        extracted_data={
            "upi_ids": ["fraudster@paytm"],
            "account_numbers": ["1234567890"],
            "ifsc_codes": [],
            "phone_numbers": ["+91 9876543210"],
            "links": []
        },
        risk_level="🔴 HIGH"
    )

    # Test: Read stats
    stats = db.get_stats()
    print("📊 Stats:", stats)

    # Test: Generate report
    report = db.generate_report("test_session_001")
    print("\n📄 Report:", report)

    # Cleanup test data
    db.clear_all()
    print("\n✅ Database test passed!")