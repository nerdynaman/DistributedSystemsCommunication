# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Buyer.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x42uyer.proto\x12\x05\x62uyer\"+\n\x13NotificationRequest\x12\x14\n\x0cNotification\x18\x01 \x01(\t\"m\n\x14NotificationResponse\x12\x32\n\x06status\x18\x01 \x01(\x0e\x32\".buyer.NotificationResponse.Status\"!\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\n\n\x06\x46\x41ILED\x10\x01\x32V\n\x05\x42uyer\x12M\n\x12Notification_Print\x12\x1a.buyer.NotificationRequest\x1a\x1b.buyer.NotificationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Buyer_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_NOTIFICATIONREQUEST']._serialized_start=22
  _globals['_NOTIFICATIONREQUEST']._serialized_end=65
  _globals['_NOTIFICATIONRESPONSE']._serialized_start=67
  _globals['_NOTIFICATIONRESPONSE']._serialized_end=176
  _globals['_NOTIFICATIONRESPONSE_STATUS']._serialized_start=143
  _globals['_NOTIFICATIONRESPONSE_STATUS']._serialized_end=176
  _globals['_BUYER']._serialized_start=178
  _globals['_BUYER']._serialized_end=264
# @@protoc_insertion_point(module_scope)