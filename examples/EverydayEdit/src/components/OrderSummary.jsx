import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function OrderSummary({subtotal=0,delivery=0}) { return <View style={{padding:20,borderRadius:16,backgroundColor:'#f4eefb',gap:12}}><Text>Subtotal: Rs. {subtotal.toLocaleString()}</Text><Text>Delivery: Rs. {delivery.toLocaleString()}</Text><Text style={{fontWeight:'800',fontSize:20}}>Total: Rs. {(subtotal+delivery).toLocaleString()}</Text></View>; }
