# 邮件验证API使用示例

## 概述

本文档提供了邮件验证注册功能的完整API使用示例，包括发送验证码、验证验证码和用户注册的完整流程。

## API端点列表

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/email/send-verification` | 发送邮箱验证码 |
| POST | `/api/email/verify-code` | 验证邮箱验证码 |
| POST | `/api/email/register` | 使用邮箱验证注册用户 |
| POST | `/api/email/resend-verification` | 重新发送验证码 |
| GET | `/api/email/check-email/{email}` | 检查邮箱可用性 |

## 完整注册流程示例

### 1. 检查邮箱可用性

**请求：**
```bash
GET /api/email/check-email/user@example.com
```

**响应：**
```json
{
    "email": "user@example.com",
    "available": true,
    "message": "邮箱可用"
}
```

### 2. 发送验证码

**请求：**
```bash
POST /api/email/send-verification
Content-Type: application/json

{
    "email": "user@example.com"
}
```

**响应：**
```json
{
    "success": true,
    "message": "验证码已发送到 user@example.com，请查收邮件",
    "email": "user@example.com"
}
```

### 3. 验证验证码

**请求：**
```bash
POST /api/email/verify-code
Content-Type: application/json

{
    "email": "user@example.com",
    "code": "123456"
}
```

**响应：**
```json
{
    "success": true,
    "message": "邮箱验证成功",
    "email": "user@example.com"
}
```

### 4. 完成用户注册

**请求：**
```bash
POST /api/email/register
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123",
    "full_name": "测试用户",
    "role_key": "restorer",
    "email": "user@example.com",
    "phone": "13800138000",
    "unit": "测试单位",
    "code": "123456"
}
```

**响应：**
```json
{
    "user_id": 1,
    "username": "testuser",
    "full_name": "测试用户",
    "role_id": 2,
    "role_name": "修复专家",
    "role_key": "restorer",
    "email": "user@example.com",
    "phone": "13800138000",
    "unit": "测试单位",
    "is_active": true,
    "email_verified": true,
    "email_verified_at": "2025-01-09T10:00:00Z",
    "created_at": "2025-01-09T10:00:00Z"
}
```

## JavaScript前端集成示例

### 1. 发送验证码

```javascript
async function sendVerificationCode(email) {
    try {
        const response = await fetch('/api/email/send-verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('验证码已发送，请查收邮件');
            return true;
        } else {
            alert('发送失败：' + result.message);
            return false;
        }
    } catch (error) {
        console.error('发送验证码失败:', error);
        alert('网络错误，请重试');
        return false;
    }
}
```

### 2. 验证验证码

```javascript
async function verifyCode(email, code) {
    try {
        const response = await fetch('/api/email/verify-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: email, 
                code: code 
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('验证码验证成功');
            return true;
        } else {
            alert('验证失败：' + result.message);
            return false;
        }
    } catch (error) {
        console.error('验证码验证失败:', error);
        alert('网络错误，请重试');
        return false;
    }
}
```

### 3. 用户注册

```javascript
async function registerUser(userData) {
    try {
        const response = await fetch('/api/email/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('注册成功！欢迎加入系统');
            // 跳转到登录页面或直接登录
            return result;
        } else {
            alert('注册失败：' + result.detail);
            return null;
        }
    } catch (error) {
        console.error('注册失败:', error);
        alert('网络错误，请重试');
        return null;
    }
}
```

### 4. 完整的注册表单处理

```javascript
class EmailRegistrationForm {
    constructor() {
        this.email = '';
        this.verificationCode = '';
        this.isEmailVerified = false;
    }
    
    // 检查邮箱可用性
    async checkEmailAvailability(email) {
        try {
            const response = await fetch(`/api/email/check-email/${email}`);
            const result = await response.json();
            return result.available;
        } catch (error) {
            console.error('检查邮箱失败:', error);
            return false;
        }
    }
    
    // 发送验证码
    async sendVerificationCode() {
        if (!this.email) {
            alert('请先输入邮箱地址');
            return false;
        }
        
        // 检查邮箱可用性
        const isAvailable = await this.checkEmailAvailability(this.email);
        if (!isAvailable) {
            alert('该邮箱已被注册');
            return false;
        }
        
        return await sendVerificationCode(this.email);
    }
    
    // 验证验证码
    async verifyCode() {
        if (!this.verificationCode) {
            alert('请输入验证码');
            return false;
        }
        
        const success = await verifyCode(this.email, this.verificationCode);
        if (success) {
            this.isEmailVerified = true;
        }
        return success;
    }
    
    // 完成注册
    async register(userData) {
        if (!this.isEmailVerified) {
            alert('请先验证邮箱');
            return false;
        }
        
        const registrationData = {
            ...userData,
            email: this.email,
            code: this.verificationCode
        };
        
        return await registerUser(registrationData);
    }
}

// 使用示例
const registrationForm = new EmailRegistrationForm();

// 绑定事件
document.getElementById('email-input').addEventListener('blur', async (e) => {
    registrationForm.email = e.target.value;
});

document.getElementById('send-code-btn').addEventListener('click', async () => {
    await registrationForm.sendVerificationCode();
});

document.getElementById('verify-code-btn').addEventListener('click', async () => {
    registrationForm.verificationCode = document.getElementById('code-input').value;
    await registrationForm.verifyCode();
});

document.getElementById('register-btn').addEventListener('click', async () => {
    const userData = {
        username: document.getElementById('username-input').value,
        password: document.getElementById('password-input').value,
        full_name: document.getElementById('fullname-input').value,
        role_key: document.getElementById('role-select').value,
        phone: document.getElementById('phone-input').value,
        unit: document.getElementById('unit-input').value
    };
    
    await registrationForm.register(userData);
});
```

## Python客户端示例

### 1. 使用requests库

```python
import requests
import json

class EmailRegistrationClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def check_email_availability(self, email):
        """检查邮箱可用性"""
        response = requests.get(f"{self.base_url}/api/email/check-email/{email}")
        return response.json()
    
    def send_verification_code(self, email):
        """发送验证码"""
        data = {"email": email}
        response = requests.post(
            f"{self.base_url}/api/email/send-verification",
            json=data
        )
        return response.json()
    
    def verify_code(self, email, code):
        """验证验证码"""
        data = {"email": email, "code": code}
        response = requests.post(
            f"{self.base_url}/api/email/verify-code",
            json=data
        )
        return response.json()
    
    def register_user(self, user_data):
        """注册用户"""
        response = requests.post(
            f"{self.base_url}/api/email/register",
            json=user_data
        )
        return response.json()

# 使用示例
client = EmailRegistrationClient()

# 1. 检查邮箱
email = "test@example.com"
result = client.check_email_availability(email)
print(f"邮箱可用性: {result}")

# 2. 发送验证码
result = client.send_verification_code(email)
print(f"发送验证码: {result}")

# 3. 验证验证码（需要用户输入）
code = input("请输入验证码: ")
result = client.verify_code(email, code)
print(f"验证结果: {result}")

# 4. 注册用户
if result.get("success"):
    user_data = {
        "username": "testuser",
        "password": "password123",
        "full_name": "测试用户",
        "role_key": "restorer",
        "email": email,
        "phone": "13800138000",
        "unit": "测试单位",
        "code": code
    }
    
    result = client.register_user(user_data)
    print(f"注册结果: {result}")
```

## 错误处理

### 常见错误码和解决方案

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 400 | 邮箱格式不正确 | 检查邮箱地址格式 |
| 400 | 该邮箱已被注册 | 使用其他邮箱地址 |
| 400 | 验证码格式不正确 | 确保输入6位数字 |
| 400 | 验证码错误或已过期 | 重新发送验证码 |
| 400 | 用户名已存在 | 使用其他用户名 |
| 400 | 无效的角色 | 使用有效的角色键值 |
| 500 | 邮件发送失败 | 检查邮件服务配置 |

### 错误响应示例

```json
{
    "detail": "验证码错误或已过期"
}
```

## 安全注意事项

1. **验证码有效期**：验证码默认10分钟有效，过期后需要重新发送
2. **尝试次数限制**：每个验证码最多尝试5次，超过后自动失效
3. **邮箱唯一性**：系统会检查邮箱是否已被注册
4. **用户名唯一性**：系统会检查用户名是否已存在
5. **密码强度**：密码至少6个字符
6. **角色验证**：只能使用系统中定义的角色键值

## 测试建议

1. **功能测试**：测试完整的注册流程
2. **边界测试**：测试无效邮箱、过期验证码等边界情况
3. **并发测试**：测试同时发送多个验证码的情况
4. **安全测试**：测试验证码暴力破解防护
5. **邮件测试**：确保邮件能正常发送和接收

## 作者信息

- **作者**: 王梓涵
- **邮箱**: wangzh011031@163.com
- **时间**: 2025年


