import React from 'react';
import {View,Text,Pressable,TextInput,StyleSheet} from 'react-native';
export default function SectionHeading({title='The collection',actionLabel='See all',onAction,color='#302338'}) { return <View style={{flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginVertical:18}}><Text style={{fontSize:24,fontWeight:'700',color}}>{title}</Text>{onAction&&<Pressable accessibilityRole='button' onPress={onAction}><Text style={{color:'#7856d8'}}>{actionLabel}</Text></Pressable>}</View>; }
