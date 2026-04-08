# -*- coding: UTF-8 -*-
# @Time     : 2026/4/4
# @Author   : Li
# @File     : models.py


from datetime import datetime
from libs.config import db


class Switch(db.Model):
    __tablename__ = 'switch'
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False)
    capabilities = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'vendor': self.vendor,
            'model': self.model,
            'description': self.description,
            'capabilities': self.capabilities
        }


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    unit_no = db.Column(db.String(20), nullable=False)
    unit_sn = db.Column(db.String(50), nullable=False, unique=True)
    user = db.Column(db.String(20), nullable=False)
    unit_phase = db.Column(db.String(20), nullable=False)
    project_code = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'unit_no': self.unit_no,
            'unit_sn': self.unit_sn,
            'user': self.user,
            'unit_phase': self.unit_phase,
            'project_code': self.project_code
        }


class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    unit_no = db.Column(db.String(20), nullable=False)
    unit_sn = db.Column(db.String(50), nullable=False, unique=True)
    user = db.Column(db.String(20), nullable=False)
    unit_phase = db.Column(db.String(20), nullable=False)
    unit_bundle = db.Column(db.String(20), nullable=False)
    project_code = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'unit_no': self.unit_no,
            'unit_sn': self.unit_sn,
            'user': self.user,
            'unit_phase': self.unit_phase,
            'project_code': self.project_code,
            'unit_bundle': self.unit_bundle
        }


class Cable(db.Model):
    __tablename__ = 'cable'
    id = db.Column(db.Integer, primary_key=True)
    cable_info = db.Column(db.String(100), nullable=False, unique=True)


class TestGroup(db.Model):
    __tablename__ = 'test_group'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    switch_id = db.Column(db.Integer, db.ForeignKey('switch.id'))
    cable_id = db.Column(db.Integer, db.ForeignKey('cable.id'))
    status = db.Column(db.String(50), default='ready')   # ready, running, completed
    test_config = db.Column(db.JSON, nullable=True, default={})
    modal_config = db.Column(db.JSON, nullable=True, default={})
    test_bundle = db.Column(db.String(100), default='')

    # relationship
    client = db.relationship('Client')
    server = db.relationship('Server')
    switch = db.relationship('Switch')
    cable = db.relationship('Cable')


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    switch_model = db.Column(db.String(200), nullable=False, unique=True)
    server_no = db.Column(db.String(20), nullable=False)
    server_sn = db.Column(db.String(50))
    server_ethernet_info = db.Column(db.String(200))
    server_phase = db.Column(db.String(20), nullable=False)
    server_project_code = db.Column(db.String(20), nullable=False)
    server_os_version = db.Column(db.String(50), nullable=False)
    server_bundle = db.Column(db.String(20))
    server_username = db.Column(db.String(50), nullable=False)
    server_hostname = db.Column(db.String(50), nullable=False)

    client_no = db.Column(db.String(20), nullable=False)
    client_sn = db.Column(db.String(50))
    client_ethernet_info = db.Column(db.String(200))
    client_phase = db.Column(db.String(20), nullable=False)
    client_project_code = db.Column(db.String(20), nullable=False)
    client_os_version = db.Column(db.String(50), nullable=False)
    client_bundle = db.Column(db.String(20))
    client_username = db.Column(db.String(50), nullable=False)
    client_hostname = db.Column(db.String(50), nullable=False)

    cable = db.Column(db.String(100), nullable=False)
    eee_status = db.Column(db.String(100))

    ping_test = db.Column(db.String(20))
    sleep_test = db.Column(db.String(20))
    restart_test = db.Column(db.String(20))
    shutdown_test = db.Column(db.String(20))

    mtu1500_autoselect_tcp = db.Column(db.String(200))
    mtu1500_autoselect_udp = db.Column(db.String(200))
    mtu1500_100_tcp = db.Column(db.String(200))
    mtu1500_100_udp = db.Column(db.String(200))
    mtu1500_1g_tcp = db.Column(db.String(200))
    mtu1500_1g_udp = db.Column(db.String(200))
    mtu1500_2500_tcp = db.Column(db.String(200))
    mtu1500_2500_udp = db.Column(db.String(200))
    mtu1500_5g_tcp = db.Column(db.String(200))
    mtu1500_5g_udp = db.Column(db.String(200))
    mtu1500_10g_tcp = db.Column(db.String(200))
    mtu1500_10g_udp = db.Column(db.String(200))

    mtu9000_1g_tcp = db.Column(db.String(200))
    mtu9000_1g_udp = db.Column(db.String(200))
    mtu9000_2500_tcp = db.Column(db.String(200))
    mtu9000_2500_udp = db.Column(db.String(200))
    mtu9000_5g_tcp = db.Column(db.String(200))
    mtu9000_5g_udp = db.Column(db.String(200))
    mtu9000_10g_tcp = db.Column(db.String(200))
    mtu9000_10g_udp = db.Column(db.String(200))

    send_file = db.Column(db.String(100))
    receive_file = db.Column(db.String(100))
    overnight_iperf = db.Column(db.String(100))

    send_file_issue = db.Column(db.Text)
    receive_file_issue = db.Column(db.Text)
    overnight_iperf_issue = db.Column(db.Text)

    ping_test_issue = db.Column(db.Text)
    sleep_test_issue = db.Column(db.Text)
    restart_test_issue = db.Column(db.Text)
    shutdown_test_issue = db.Column(db.Text)

    autoselect_tcp_issue = db.Column(db.Text)
    autoselect_udp_issue = db.Column(db.Text)
    mtu1500_100_tcp_issue = db.Column(db.Text)
    mtu1500_100_udp_issue = db.Column(db.Text)
    mtu1500_1g_tcp_issue = db.Column(db.Text)
    mtu1500_1g_udp_issue = db.Column(db.Text)
    mtu1500_2500_tcp_issue = db.Column(db.Text)
    mtu1500_2500_udp_issue = db.Column(db.Text)
    mtu1500_5g_tcp_issue = db.Column(db.Text)
    mtu1500_5g_udp_issue = db.Column(db.Text)
    mtu1500_10g_tcp_issue = db.Column(db.Text)
    mtu1500_10g_udp_issue = db.Column(db.Text)

    mtu9000_1g_tcp_issue = db.Column(db.Text)
    mtu9000_1g_udp_issue = db.Column(db.Text)
    mtu9000_2500_tcp_issue = db.Column(db.Text)
    mtu9000_2500_udp_issue = db.Column(db.Text)
    mtu9000_5g_tcp_issue = db.Column(db.Text)
    mtu9000_5g_udp_issue = db.Column(db.Text)
    mtu9000_10g_tcp_issue = db.Column(db.Text)
    mtu9000_10g_udp_issue = db.Column(db.Text)

    update_time = db.Column(db.String(60))
    is_exported = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    current_test_item = db.Column(db.String(100))
