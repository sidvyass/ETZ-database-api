import logging
from connection import get_connection
import time
from item import Item
from general_class import TableManger
import re

logger = logging.getLogger().getChild("MAIL")

def send_mail(subject, body, recipient):
    """Sends an email using the database inbuilt function. Done using SQL query"""
    t_sql_command = f"""
    EXEC msdb.dbo.sp_send_dbmail @profile_name = "MIE Notifications",
                        @recipients = "{recipient}",
                        @subject = "{subject}",
                        @body = "{body}";
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(t_sql_command)

        logger.info(f"Email command executed. Recipient -> {recipient}. SENT STATUS PENDING")

        time.sleep(5)  # we check the status after 5 seconds
        query = "SELECT IDENT_CURRENT('msdb.dbo.sysmail_allitems')"
        cursor.execute(query)
        pk = cursor.fetchone()[0]
        sent_status_query = "SELECT sent_status FROM msdb.dbo.sysmail_allitems WHERE mailitem_id = ?"
        cursor.execute(sent_status_query, pk)
        
        status = cursor.fetchone()[0] 
        if status == "sent":
            logger.info(f"Eamil Sent. SENT STATUS CONFIRMED")
        elif status == "failed":
            logger.error(f"Email failed. recipient: {recipient}")
        else:
            logger.critical("Unknown error. Message not delivered")


def get_emails_for_op_or_material(material_code=None, group_id=None):
    """Gets the email IDs of vendors to get work done from
    If no material is passed and only group ID is provided, the type of material or OP will 
    be pulled from description of the item. If a group_id is passed then the program will directly go
    and find all the emails from that group ID.
    params: need to provide at least one
    material_code: name of the material or process that goes to OP or supplier
    group_id: ID of the group can see on Mie Trak
    """
    if (material_code is None and group_id is None) or (material_code is not None and group_id is not None):
        raise ValueError("Please provide exactly one of material_code or group_id.")
    material_code_dict = {  # as per group IDs in Mie Trak
        "HT-STL": [3764, "Steel HT"],  # naming convention is still not done 
        "HT": [3755, "OP Finish"],
        "AL": [3744, "Aluminum"],  # no description in the party buyer table
        "STL": [3747, "Steel"],
        "TI": ["Titanium"]
    }
    if not group_id:
        item_table = Item()
        value = item_table.get("description", PartNumber=material_code)[0][0]
        for key in material_code_dict.keys():
            if re.match(rf"\b{key}\b", value):
                group_id = material_code_dict[key][0]  # ID to pull all the relevant emails from
                break
    assert group_id
    party_buyer = TableManger("PartyBuyer")
    output = party_buyer.get("BuyerFK", PartyFK=group_id)
    buyerfks = [fk[0] for fk in output]  # suppliers to email
    party = TableManger("Party")
    email_list = []
    for fk in buyerfks:
        email = party.get("Email", PartyPK=fk)
        email_list.append(email[0][0])
    print(f"This email list is for group ID - {group_id}")
    return email_list


if __name__ == "__main__":
    print(get_emails_for_op_or_material("0.016 2024-T3 AMS-QQ-A-250/5"))