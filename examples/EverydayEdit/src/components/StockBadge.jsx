import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function StockBadge({stock=5}) { return <Text style={{color:stock>0?'#518365':'#b75f4c',fontSize:12}}>{stock>0?stock+' in stock':'Out of stock'}</Text>; }
