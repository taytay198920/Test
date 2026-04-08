# -*- coding: UTF-8 -*-
# @Time     : 2026/4/4
# @Author   : Li
# @File     : app.py.py


from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_cors import CORS
from sqlalchemy import and_

from libs.handle_log import log
from libs.handle_path import *
from libs.config import db, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, APP_SECRET_KEY
from libs.cli import execute
from libs.models import Switch, Server, Cable, Client, TestGroup, Result


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = APP_SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()
    # if TestGroup.query.count() == 0:
    #     group = TestGroup(client_id=1, server_id=1, switch_id=1, cable_id=1)
    #     db.session.add(group)
    #     db.session.commit()

@app.route('/', methods=['GET'])
def index():
    test_groups = TestGroup.query.order_by(TestGroup.id).all()
    clients = Client.query.order_by(Client.id).all()
    servers = Server.query.order_by(Server.id).all()
    switches = Switch.query.order_by(Switch.id).all()
    cables = Cable.query.order_by(Cable.id).all()
    return render_template("index.html", current_url="index", groups=test_groups, clients=clients,
                           servers=servers, switches=switches, cables=cables)


@app.route('/api/new_group', methods=['POST'])
def new_group():
    try:
        new_test_group = TestGroup(client_id='', server_id='', switch_id='', cable_id='')
        db.session.add(new_test_group)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        flash("New test group add failed, please try again", "error")
        return redirect(url_for('index'))

@app.route('/api/groups/delete/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    try:
        group = TestGroup.query.get_or_404(group_id)
        db.session.delete(group)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        flash("Group delete failed, please try again", "error")
        return redirect(url_for('index'))

@app.route('/api/test/run', methods=['POST'])
def run_test():
    """运行测试的接口"""
    try:
        # 保存modal的配置
        modal_config = request.get_json()
        log.info("config data: %s", modal_config)

        # 保存data转换后的测试配置格式
        test_config = {}
        if modal_config['basic_test']:
            test_config['basic_test'] = modal_config['basic_test']
        if modal_config['power_management']:
            test_config['power_management'] = modal_config['power_management']
        if modal_config['mtu1500']['protocols']:
            test_config['mtu1500'] = modal_config['mtu1500']
        if modal_config['mtu9000']['protocols']:
            test_config['mtu9000'] = modal_config['mtu9000']

        log.info("test config: %s", test_config)

        group_id = modal_config['group_id']
        hardware = modal_config['hardware']
        # 更新测试组状态
        test_group = TestGroup.query.get_or_404(group_id)
        if test_group:
            test_group.status = 'running'

            # 更新硬件配置
            if hardware.get('client_id'):
                test_group.client_id = hardware.get('client_id')
            if hardware.get('server_id'):
                test_group.server_id = hardware.get('server_id')
            if hardware.get('switch_id'):
                test_group.switch_id = hardware.get('switch_id')
            if hardware.get('cable_id'):
                test_group.cable_id = hardware.get('cable_id')
            if hardware.get('test_bundle'):
                test_group.test_bundle = hardware.get('test_bundle')
            test_group.test_config = test_config
            test_group.modal_config = modal_config

        db.session.commit()

        # 这里添加实际的测试执行逻辑
        # 例如：根据配置启动异步测试任务
        # from libs.test_runner import run_test_async
        # run_test_async(group_id, config_data)

        return jsonify({
            'success': True,
            'message': f'Test started for group {group_id}',
            'config_received': modal_config
        })

    except Exception as e:
        log.error(f"Error running test: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/switches', methods=['GET'])
def switches_management():
    page = request.args.get('page', 1, type=int)
    pagination = Switch.query.order_by(Switch.id).paginate(page=page, per_page=100, error_out=False)
    switches = pagination.items
    return render_template("switch_management.html", current_url="management", switches=switches,
                           pagination=pagination)

@app.route('/api/switches/add', methods=['POST'])
def add_switch():
    vendor = request.form['vendor'].strip()
    model = request.form['model'].strip()
    description = request.form['description'].strip()
    capabilities = request.form['capabilities'].strip()
    log.info(vendor, model, description, capabilities)
    new_switch = Switch(vendor=vendor, model=model, description=description, capabilities=capabilities)
    try:
        db.session.add(new_switch)
        db.session.commit()
        flash('Switch added successfully', 'success')
        return redirect(url_for('switches_management'))
    except Exception as e:
        flash(f"Switch added fail, fail reason: {str(e)}", 'error')
        log.error(f"Switch added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('switches_management'))

@app.route('/api/switches/edit/<int:switch_id>', methods=["POST"])
def edit_switch(switch_id):
    switch = Switch.query.get_or_404(switch_id)
    vendor = request.form['vendor']
    model = request.form['model']
    description = request.form['description']
    capabilities = request.form['capabilities']
    switch.vendor = vendor.strip()
    switch.model = model.strip()
    switch.description = description.strip()
    switch.capabilities = capabilities.strip()
    try:
        db.session.commit()
        flash('Switch updated successfully', 'success')
        return redirect(url_for('switches_management'))
    except Exception as e:
        flash(f"Switch updated fail, fail reason: {str(e)}", 'error')
        log.error(f"Switch updated fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('switches_management'))

@app.route('/api/switches/delete/<int:switch_id>', methods=["POST"])
def delete_switch(switch_id):
    switch = Switch.query.get_or_404(switch_id)
    db.session.delete(switch)
    db.session.commit()
    flash('Switch deleted successfully', 'success')
    return redirect(url_for('switches_management'))

@app.route('/api/servers', methods=['GET'])
def servers_management():
    page = request.args.get('page', 1, type=int)
    pagination = Server.query.order_by(Server.id).paginate(page=page, per_page=100, error_out=False)
    servers = pagination.items
    return render_template("server_management.html", current_url="management", servers=servers,
                           pagination=pagination)

@app.route('/api/servers/add', methods=['POST'])
def add_server():
    unit_no = request.form['unit_no'].strip()
    unit_sn = request.form['unit_sn'].strip()
    user = request.form['user'].strip()
    unit_phase = request.form['unit_phase'].strip()
    unit_bundle = request.form['unit_bundle'].strip()
    project_code = request.form['project_code'].strip()
    new_server = Server(unit_no=unit_no, unit_sn=unit_sn, user=user, unit_phase=unit_phase, unit_bundle=unit_bundle,
                        project_code=project_code)
    try:
        db.session.add(new_server)
        db.session.commit()
        flash('Server added successfully', 'success')
        return redirect(url_for('servers_management'))
    except Exception as e:
        flash(f"Server added fail, fail reason: {str(e)}", 'error')
        log.error(f"Server added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('servers_management'))

@app.route('/api/servers/edit/<int:server_id>', methods=["POST"])
def edit_server(server_id):
    server = Server.query.get_or_404(server_id)
    unit_no = request.form['new_no'].strip()
    unit_sn = request.form['new_sn'].strip()
    user = request.form['new_user'].strip()
    unit_phase = request.form['new_phase'].strip()
    unit_bundle = request.form['new_bundle'].strip()
    project_code = request.form['new_code'].strip()
    server.unit_no = unit_no
    server.unit_sn = unit_sn
    server.user = user
    server.unit_phase = unit_phase
    server.unit_bundle = unit_bundle
    server.project_code = project_code
    try:
        db.session.commit()
        flash('Server updated successfully', 'success')
        return redirect(url_for('servers_management'))
    except Exception as e:
        flash(f"Server updated fail, fail reason: {str(e)}", 'error')
        log.error(f"Server updated fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('servers_management'))

@app.route('/api/servers/delete/<int:server_id>', methods=["POST"])
def delete_server(server_id):
    server = Server.query.get_or_404(server_id)
    db.session.delete(server)
    db.session.commit()
    flash('Server deleted successfully', 'success')
    return redirect(url_for('servers_management'))

@app.route('/api/cables', methods=['GET'])
def cables_management():
    page = request.args.get('page', 1, type=int)
    pagination = Cable.query.order_by(Cable.id).paginate(page=page, per_page=100, error_out=False)
    cables = pagination.items
    return render_template("cable_management.html", current_url="management",
                           cables=cables, pagination=pagination)

@app.route('/api/cables/add', methods=['POST'])
def add_cable():
    cable_info = request.form['cable_info'].strip()
    new_cable = Cable(cable_info=cable_info)
    try:
        db.session.add(new_cable)
        db.session.commit()
        flash('Cable added successfully', 'success')
        return redirect(url_for('cables_management'))
    except Exception as e:
        flash(f"Cable added fail, fail reason: {str(e)}", 'error')
        log.error(f"Cable added fail, fail reason: {str(e)}")
        return redirect(url_for('cables_management'))

@app.route('/api/cables/delete/<int:cable_id>', methods=["POST"])
def delete_cable(cable_id):
    cable = Cable.query.get_or_404(cable_id)
    db.session.delete(cable)
    db.session.commit()
    flash('Cable deleted successfully', 'success')
    return redirect(url_for('cables_management'))

@app.route('/api/clients', methods=['GET'])
def clients_management():
    page = request.args.get('page', 1, type=int)
    pagination = Client.query.order_by(Client.id).paginate(page=page, per_page=100, error_out=False)
    clients = pagination.items
    return render_template("client_management.html", current_url="management",
                           clients=clients, pagination=pagination)

@app.route('/api/clients/add', methods=['POST'])
def add_client():
    unit_no = request.form['unit_no'].strip()
    unit_sn = request.form['unit_sn'].strip()
    user = request.form['user'].strip()
    unit_phase = request.form['unit_phase'].strip()
    project_code = request.form['project_code'].strip()
    new_client = Client(unit_no=unit_no, unit_sn=unit_sn, user=user, unit_phase=unit_phase, project_code=project_code)
    try:
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully', 'success')
        return redirect(url_for('clients_management'))
    except Exception as e:
        flash(f"Client added fail, fail reason: {str(e)}", 'error')
        log.error(f"Client added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('clients_management'))

@app.route('/api/clients/edit/<int:client_id>', methods=["POST"])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    unit_no = request.form['new_no'].strip()
    unit_sn = request.form['new_sn'].strip()
    user = request.form['new_user'].strip()
    unit_phase = request.form['new_phase'].strip()
    project_code = request.form['new_code'].strip()
    client.unit_no = unit_no
    client.unit_sn = unit_sn
    client.user = user
    client.unit_phase = unit_phase
    client.project_code = project_code
    try:
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('clients_management'))
    except Exception as e:
        flash(f"Client updated fail, fail reason: {str(e)}", 'error')
        log.error(f"Client updated fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('clients_management'))

@app.route('/api/clients/delete/<int:client_id>', methods=["POST"])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully', 'success')
    return redirect(url_for('clients_management'))

@app.route('/api/monitors', methods=['GET'])
def monitors():
    page = request.args.get('page', 1, type=int)
    pagination = Result.query.filter_by(is_exported=False).order_by(Result.id).paginate(page=page, per_page=100,
                                                                                               error_out=False)
    test_results = pagination.items
    return render_template("monitor.html", current_url="monitor", test_results=test_results, pagination=pagination)

@app.route('/api/edit_basic_issues/<int:result_id>', methods=["POST"])
def edit_basic_issues(result_id):
    result = Result.query.get_or_404(result_id)
    if request.form["ping_test"]:
        result.ping_test_issue = request.form["ping_test"]
    if request.form['restart_test']:
        result.restart_test_issue = request.form["restart_test"]
    if request.form['shutdown_test']:
        result.shutdown_test_issue = request.form["shutdown_test"]
    if request.form['sleep_test']:
        result.sleep_test_issue = request.form["sleep_test"]
    try:
        db.session.commit()
        flash('Issues added successfully', 'success')
        return redirect(url_for('monitors'))
    except Exception as e:
        flash(f"Issues added fail, fail reason: {str(e)}", 'error')
        log.error(f"Issues added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('monitors'))

@app.route('/api/edit_mtu1500_issues/<int:result_id>', methods=["POST"])
def edit_mtu1500_issues(result_id):
    result = Result.query.get_or_404(result_id)
    if request.form["autoselect_tcp"]:
        result.autoselect_tcp_issue = request.form["autoselect_tcp"]
    if request.form["autoselect_udp"]:
        result.autoselect_udp_issue = request.form["autoselect_udp"]
    if request.form["mtu1500_100m_tcp"]:
        result.mtu1500_100_tcp_issue = request.form["mtu1500_100m_tcp"]
    if request.form["mtu1500_100m_udp"]:
        result.mtu1500_100_udp_issue = request.form["mtu1500_100m_udp"]
    if request.form["mtu1500_1g_tcp"]:
        result.mtu1500_1g_tcp_issue = request.form["mtu1500_1g_tcp"]
    if request.form["mtu1500_1g_udp"]:
        result.mtu1500_1g_udp_issue = request.form["mtu1500_1g_udp"]
    if request.form["mtu1500_2500m_tcp"]:
        result.mtu1500_2500_tcp_issue = request.form["mtu1500_2500m_tcp"]
    if request.form["mtu1500_2500m_udp"]:
        result.mtu1500_2500_udp_issue = request.form["mtu1500_2500m_udp"]
    if request.form["mtu1500_5g_tcp"]:
        result.mtu1500_5g_tcp_issue = request.form["mtu1500_5g_tcp"]
    if request.form["mtu1500_5g_udp"]:
        result.mtu1500_5g_udp_issue = request.form["mtu1500_5g_udp"]
    if request.form["mtu1500_10g_tcp"]:
        result.mtu1500_10g_tcp_issue = request.form["mtu1500_10g_tcp"]
    if request.form["mtu1500_10g_udp"]:
        result.mtu1500_10g_udp_issue = request.form["mtu1500_10g_udp"]

    try:
        db.session.commit()
        flash('Issues added successfully', 'success')
        return redirect(url_for('monitors'))
    except Exception as e:
        flash(f"Issues added fail, fail reason: {str(e)}", 'error')
        log.error(f"Issues added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('monitors'))

@app.route('/api/edit_mtu9000_issues/<int:result_id>', methods=["POST"])
def edit_mtu9000_issues(result_id):
    result = Result.query.get_or_404(result_id)
    if request.form["mtu9000_1g_tcp"]:
        result.mtu9000_1g_tcp_issue = request.form["mtu9000_1g_tcp"]
    if request.form["mtu9000_1g_udp"]:
        result.mtu9000_1g_udp_issue = request.form["mtu9000_1g_udp"]
    if request.form["mtu9000_2500m_tcp"]:
        result.mtu9000_2500_tcp_issue = request.form["mtu9000_2500m_tcp"]
    if request.form["mtu9000_2500m_udp"]:
        result.mtu9000_2500_udp_issue = request.form["mtu9000_2500m_udp"]
    if request.form["mtu9000_5g_tcp"]:
        result.mtu9000_5g_tcp_issue = request.form["mtu9000_5g_tcp"]
    if request.form["mtu9000_5g_udp"]:
        result.mtu9000_5g_udp_issue = request.form["mtu9000_5g_udp"]
    if request.form["mtu9000_10g_tcp"]:
        result.mtu9000_10g_tcp_issue = request.form["mtu9000_10g_tcp"]
    if request.form["mtu9000_10g_udp"]:
        result.mtu9000_10g_udp_issue = request.form["mtu9000_10g_udp"]
    try:
        db.session.commit()
        flash('Issues added successfully', 'success')
        return redirect(url_for('monitors'))
    except Exception as e:
        flash(f"Issues added fail, fail reason: {str(e)}", 'error')
        log.error(f"Issues added fail, fail reason: {str(e)}")
        db.session.rollback()
        return redirect(url_for('monitors'))

@app.route("/api/edit_overnight_issues/<int:result_id>", methods=["POST"])
def edit_overnight_issues(result_id):
    result = Result.query.get_or_404(result_id)
    try:
        if request.form["send_file_issue"]:
            result.send_file_issue = request.form["send_file_issue"]
        if request.form["receive_file_issue"]:
            result.receive_file_issue = request.form["receive_file_issue"]
        if request.form["iperf_overnight"]:
            result.iperf_overnight = request.form["iperf_overnight"]

        db.session.commit()
        flash("Issues updated successfully!", "success")
        return redirect(url_for('monitors'))
    except Exception as e:
        db.session.rollback()
        log.error(f"update overnight issues error: {e}")
        return redirect(url_for('monitors'))

@app.route('/api/add_test_result', methods=["POST"])
def add_test_result():
    new_data = request.get_json()
    try:
        switch_model = new_data["switch_model"]
        server_no = new_data["server_no"]
        server_sn = new_data["server_sn"]
        server_ethernet_info = new_data["server_ethernet_info"]
        server_phase = new_data["server_phase"]
        server_project_code = new_data["server_project_code"]
        server_os_version = new_data["server_os_version"]
        server_bundle = new_data.get("server_bundle", '')
        server_username = new_data["server_username"]
        server_hostname = new_data["server_hostname"]
        client_no = new_data["client_no"]
        client_sn = new_data["client_sn"]
        client_ethernet_info = new_data["client_ethernet_info"]
        client_phase = new_data["client_phase"]
        client_project_code = new_data["client_project_code"]
        client_os_version = new_data["client_os_version"]
        client_bundle = new_data.get("client_bundle", '')
        client_username = new_data["client_username"]
        client_hostname = new_data["client_hostname"]
        cable = new_data["cable"]
        eee_status = new_data["eee_status"]
        new_result = Result(switch_model=switch_model, server_no=server_no, server_sn=server_sn,
                            server_ethernet_info=server_ethernet_info, server_phase=server_phase,
                            server_project_code=server_project_code, server_os_version=server_os_version,
                            server_bundle=server_bundle, server_username=server_username,
                            server_hostname=server_hostname, client_no=client_no, client_sn=client_sn,
                            client_ethernet_info=client_ethernet_info, client_phase=client_phase,
                            client_project_code=client_project_code, client_os_version=client_os_version,
                            client_bundle=client_bundle, client_username=client_username,
                            client_hostname=client_hostname, cable=cable, eee_status=eee_status)
        db.session.add(new_result)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Test result added successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        log.error(f"add_test_result fail, fail reason: {str(e)}", 'error')
        return jsonify({
            "status": "failure",
            "message": str(e)
        }), 500

@app.route('/api/update_test_result', methods=["POST"])
def update_test_result():
    data = request.get_json()
    log.info(f"update data: {data}")
    try:
        switch_model = data["switch_model"]
        client_os_version = data["client_os_version"]

        ping_test = data.get("ping_test")
        sleep_test = data.get("sleep_test")
        restart_test = data.get("restart_test")
        shutdown_test = data.get("shutdown_test")
        mtu1500_autoselect_tcp = data.get("mtu1500_autoselect_tcp")
        mtu1500_autoselect_udp = data.get("mtu1500_autoselect_udp")
        mtu1500_100_tcp = data.get("mtu1500_100_tcp")
        mtu1500_100_udp = data.get("mtu1500_100_udp")
        mtu1500_1g_tcp = data.get("mtu1500_1g_tcp")
        mtu1500_1g_udp = data.get("mtu1500_1g_udp")
        mtu1500_2500_tcp = data.get("mtu1500_2500_tcp")
        mtu1500_2500_udp = data.get("mtu1500_2500_udp")
        mtu1500_5g_tcp = data.get("mtu1500_5g_tcp")
        mtu1500_5g_udp = data.get("mtu1500_5g_udp")
        mtu1500_10g_tcp = data.get("mtu1500_10g_tcp")
        mtu1500_10g_udp = data.get("mtu1500_10g_udp")
        mtu9000_1g_tcp = data.get("mtu9000_1g_tcp")
        mtu9000_1g_udp = data.get("mtu9000_1g_udp")
        mtu9000_2500_tcp = data.get("mtu9000_2500_tcp")
        mtu9000_2500_udp = data.get("mtu9000_2500_udp")
        mtu9000_5g_tcp = data.get("mtu9000_5g_tcp")
        mtu9000_5g_udp = data.get("mtu9000_5g_udp")
        mtu9000_10g_tcp = data.get("mtu9000_10g_tcp")
        mtu9000_10g_udp = data.get("mtu9000_10g_udp")
        send_file = data.get("send_file")
        receive_file = data.get("receive_file")
        overnight_iperf = data.get("overnight_iperf")
        current_test_item = data.get("current_test_item")
        update_time = data["update_time"]

        result = Result.query.filter(and_(Result.switch_model == switch_model, Result.client_os_version == client_os_version)).first()
        log.info(result)

        if ping_test:
            result.ping_test = ping_test
        if sleep_test:
            result.sleep_test = sleep_test
        if restart_test:
            result.restart_test = restart_test
        if shutdown_test:
            result.shutdown_test = shutdown_test
        if mtu1500_autoselect_tcp:
            result.mtu1500_autoselect_tcp = mtu1500_autoselect_tcp
        if mtu1500_autoselect_udp:
            result.mtu1500_autoselect_udp = mtu1500_autoselect_udp
        if mtu1500_100_tcp:
            result.mtu1500_100_tcp = mtu1500_100_tcp
        if mtu1500_100_udp:
            result.mtu1500_100_udp = mtu1500_100_udp
        if mtu1500_1g_tcp:
            result.mtu1500_1g_tcp = mtu1500_1g_tcp
        if mtu1500_1g_udp:
            result.mtu1500_1g_udp = mtu1500_1g_udp
        if mtu1500_2500_tcp:
            result.mtu1500_2500_tcp = mtu1500_2500_tcp
        if mtu1500_2500_udp:
            result.mtu1500_2500_udp = mtu1500_2500_udp
        if mtu1500_5g_tcp:
            result.mtu1500_5g_tcp = mtu1500_5g_tcp
        if mtu1500_5g_udp:
            result.mtu1500_5g_udp = mtu1500_5g_udp
        if mtu1500_10g_tcp:
            result.mtu1500_10g_tcp = mtu1500_10g_tcp
        if mtu1500_10g_udp:
            result.mtu1500_10g_udp = mtu1500_10g_udp
        if mtu9000_1g_tcp:
            result.mtu9000_1g_tcp = mtu9000_1g_tcp
        if mtu9000_1g_udp:
            result.mtu9000_1g_udp = mtu9000_1g_udp
        if mtu9000_2500_tcp:
            result.mtu9000_2500_tcp = mtu9000_2500_tcp
        if mtu9000_2500_udp:
            result.mtu9000_2500_udp = mtu9000_2500_udp
        if mtu9000_5g_tcp:
            result.mtu9000_5g_tcp = mtu9000_5g_tcp
        if mtu9000_5g_udp:
            result.mtu9000_5g_udp = mtu9000_5g_udp
        if mtu9000_10g_tcp:
            result.mtu9000_10g_tcp = mtu9000_10g_tcp
        if mtu9000_10g_udp:
            result.mtu9000_10g_udp = mtu9000_10g_udp
        if overnight_iperf:
            result.overnight_iperf = overnight_iperf
        if send_file:
            result.send_file = send_file
        if receive_file:
            result.receive_file = receive_file
        if current_test_item:
            result.current_test_item = current_test_item
        result.update_time = update_time

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "result updated successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        log.error(f"update result error: {e}")
        return jsonify({
            "status": "error",
            "message": f"update result error: {e}"
        }), 500

@app.route("/api/iperf_detail/<int:result_id>", methods=["GET"])
def iperf_detail(result_id):
    result = Result.query.get_or_404(result_id)
    return render_template("iperf_detail.html", result=result, current_url='monitor')


if __name__ == '__main__':
    with open(log_path, 'w'):
        pass
    app.run(debug=True, host='127.0.0.1', port=5002)