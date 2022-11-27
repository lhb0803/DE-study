with open('./rootkey.csv', 'r') as f:
    aws_access_key_id, aws_secret_access_key = f.read().split('\n')
    aws_access_key_id = aws_access_key_id.split('=')[1]
    aws_secret_access_key = aws_secret_access_key.split('=')[1]

print(aws_access_key_id)
print(aws_secret_access_key)