import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function DiscountBadge({percent=20}) { return <View style={{backgroundColor:'#fce9e2',padding:7,borderRadius:9,alignSelf:'flex-start'}}><Text style={{color:'#a95438',fontWeight:'700'}}>{Math.max(0,Math.min(100,percent))}% OFF</Text></View>; }
