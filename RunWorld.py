from Tiles.Configuration.World import TileServer

a = TileServer()
a.init(('127.0.0.1', 9875), 1)
a.run()
