export type Phase='wait'|'sit'|'fly'|'land'|'dead'|'city_clear'|'win';
export type Progress={city:number;level:number;pad:number;aura:number;coins:number;score:number;landings:number;unlockedMax:number;ownedShoes:string[];shoe:string;flipMode:'front'|'back';stats:{attempts:number;perfectLandings:number}};
export type Shoe={id:string;name:string;desc:string;price:number;jump:number;speed:number;spin:number;coins:number;color:string};
