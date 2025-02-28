import 'package:flutter/material.dart';

class UserProfileWidget extends StatefulWidget {
  final String userId;
  final bool isEditable;

  const UserProfileWidget({
    Key? key,
    required this.userId,
    this.isEditable = false,
  }) : super(key: key);

  @override
  _UserProfileWidgetState createState() => _UserProfileWidgetState();
}

class _UserProfileWidgetState extends State<UserProfileWidget> {
  late UserModel _user;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final userService = UserService();
      _user = await userService.getUserById(widget.userId);
    } catch (e) {
      _handleError(e);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _handleError(dynamic error) {
    // エラー処理
    print('Error loading user: $error');
    // このメソッドはこのクラス内でのみ使用
  }

  void _updateProfile() async {
    // プロフィール更新処理
    final userService = UserService();
    await userService.updateUser(_user);
    _showUpdateSuccessMessage();
  }

  void _showUpdateSuccessMessage() {
    // 更新成功メッセージを表示
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Profile updated successfully')),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildLoadingIndicator();
    }
    
    return Column(
      children: [
        _buildProfileHeader(),
        _buildProfileDetails(),
        if (widget.isEditable) _buildEditButton(),
      ],
    );
  }

  Widget _buildLoadingIndicator() {
    return Center(child: CircularProgressIndicator());
  }

  Widget _buildProfileHeader() {
    // プロフィールヘッダーを構築
    return Text('Profile');
  }

  Widget _buildProfileDetails() {
    // プロフィール詳細を構築
    return Text('Details');
  }

  Widget _buildEditButton() {
    // 編集ボタンを構築
    return ElevatedButton(
      onPressed: _updateProfile,
      child: Text('Edit'),
    );
  }
}

class UserModel {
  final String id;
  String name;
  String email;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
  });
}

class UserService {
  Future<UserModel> getUserById(String userId) async {
    // APIからユーザーデータを取得
    await Future.delayed(Duration(seconds: 1));
    return UserModel(
      id: userId,
      name: 'John Doe',
      email: 'john.doe@example.com',
    );
  }

  Future<void> updateUser(UserModel user) async {
    // ユーザーデータを更新
    await Future.delayed(Duration(seconds: 1));
  }
}