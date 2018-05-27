# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import dist_SGD_pb2 as dist__SGD__pb2


class dist_SGDStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Send_Weights = channel.unary_unary(
        '/stochastic.dist_SGD/Send_Weights',
        request_serializer=dist__SGD__pb2.WS_Update.SerializeToString,
        response_deserializer=dist__SGD__pb2.ACK.FromString,
        )
    self.Receive_Weights = channel.unary_unary(
        '/stochastic.dist_SGD/Receive_Weights',
        request_serializer=dist__SGD__pb2.WS_Update.SerializeToString,
        response_deserializer=dist__SGD__pb2.WS_Update.FromString,
        )


class dist_SGDServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Send_Weights(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Receive_Weights(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_dist_SGDServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Send_Weights': grpc.unary_unary_rpc_method_handler(
          servicer.Send_Weights,
          request_deserializer=dist__SGD__pb2.WS_Update.FromString,
          response_serializer=dist__SGD__pb2.ACK.SerializeToString,
      ),
      'Receive_Weights': grpc.unary_unary_rpc_method_handler(
          servicer.Receive_Weights,
          request_deserializer=dist__SGD__pb2.WS_Update.FromString,
          response_serializer=dist__SGD__pb2.WS_Update.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'stochastic.dist_SGD', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))