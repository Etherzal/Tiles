from Tiles.Configuration.Login import PrimaryLogin

a = PrimaryLogin()
a.init(('127.0.0.1', 6112), 1)
a.run()
