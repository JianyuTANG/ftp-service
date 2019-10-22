import client


c = client.Client()

c.username = 'anonymous'
c.password = 'e73jzTRTNqCN9PYAAjjn'
c.server_ip = "127.0.0.1"
c.server_port = 10011

print(c.username)
print(c.connect())
data = '\n'.join(c.prompt_lines)
print(data)
print('555')
